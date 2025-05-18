from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Choices

from core.choices import EnergyDirection


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
