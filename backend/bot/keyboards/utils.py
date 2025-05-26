from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Choices, QuerySet

from bot.config import config
from core.choices import EnergyDirection
from core.models import Course, Habit


async def get_pagination_buttons(
    previous_button_data: str = None,
    next_button_data: str = None,
) -> list[InlineKeyboardButton]:
    pagination_buttons = []

    if previous_button_data:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='<<',
                callback_data=previous_button_data,
            ),
        )

    if next_button_data:
        pagination_buttons.append(
            InlineKeyboardButton(text='>>', callback_data=next_button_data),
        )

    return pagination_buttons


async def keyboard_from_queryset(
    queryset: QuerySet,
    *,
    prefix: str,
    back_button_data: str = None,
    previous_button_data: str = None,
    next_button_data: str = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    async for obj in queryset:
        kb.button(text=str(obj), callback_data=f'{prefix}:{obj.pk}')

    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)

    kb.adjust(1)
    kb.row(
        *await get_pagination_buttons(
            previous_button_data,
            next_button_data,
        ),
    )
    return kb.as_markup()


async def get_paginated_keyboard(
    queryset: QuerySet,
    *,
    prefix: str = '',
    page: int = 1,
    page_size: int = config.PAGE_SIZE,
    back_button_data: str = '',
    previous_button_data: str = '',
    next_button_data: str = '',
) -> InlineKeyboardMarkup:
    total_count = await queryset.acount()
    total_pages = (total_count + page_size - 1) // page_size
    start, end = (page - 1) * page_size, page * page_size

    return await keyboard_from_queryset(
        queryset[start:end],
        prefix=prefix,
        back_button_data=back_button_data,
        previous_button_data=previous_button_data if page > 1 else None,
        next_button_data=next_button_data if page < total_pages else None,
    )


def one_button_keyboard(
    *,
    back_button_data: str = None,
    **kwargs,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(**kwargs)
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    return kb.adjust(1).as_markup()


def keyboard_from_choices(
    choices: type[Choices],
    *,
    prefix: str = '',
    back_button_data: str | None = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in choices.choices:
        kb.button(
            text=label,
            callback_data=f'{prefix}:{value}' if prefix else value,
        )
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    return kb.adjust(1).as_markup()


def get_greeting_kb(text: str):
    return one_button_keyboard(text=text, callback_data='start_survey')


def get_energy_directions_kb():
    kb = InlineKeyboardBuilder.from_markup(
        keyboard_from_choices(EnergyDirection),
    )
    kb.button(text='Выбрал', callback_data='done')
    return kb.adjust(1).as_markup()


async def get_habits_kb(client_id: int, *, page: int = 1):
    return await get_paginated_keyboard(
        Habit.objects.filter(client_id=client_id),
        prefix='habit',
        page=page,
        back_button_data='habits_menu',
        previous_button_data='habits_previous',
        next_button_data='habits_next',
    )


def get_habit_kb(habit_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Редактировать',
                    callback_data=f'update_habit:{habit_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Удалить',
                    callback_data=f'delete_habit:{habit_id}',
                ),
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data='habits'),
            ],
        ],
    )


async def get_courses_kb():
    kb = InlineKeyboardBuilder()
    async for course in Course.objects.all():
        kb.button(text=str(course), url=f'{course.url}')
    kb.button(text='Назад', callback_data='to_start')
    return kb.adjust(1).as_markup()
