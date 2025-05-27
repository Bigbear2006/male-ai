from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.utils import get_paginated_keyboard
from core.models import Habit

habits_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Добавить привычку',
                callback_data='add_habit',
            ),
        ],
        [InlineKeyboardButton(text='Все привычки', callback_data='habits')],
        [InlineKeyboardButton(text='Назад', callback_data='to_start')],
    ],
)


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
