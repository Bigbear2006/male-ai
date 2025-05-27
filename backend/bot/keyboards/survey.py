from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.utils import keyboard_from_choices
from core.choices import EnergyDirection

ages_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='до 20', callback_data='<=20'),
            InlineKeyboardButton(text='21-25', callback_data='21-25'),
            InlineKeyboardButton(text='26-30', callback_data='26-30'),
        ],
        [
            InlineKeyboardButton(text='31-35', callback_data='31-35'),
            InlineKeyboardButton(text='36-40', callback_data='36-40'),
            InlineKeyboardButton(text='41+', callback_data='41+'),
        ],
    ],
)

self_ratings_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=str(i), callback_data=str(i))
            for i in range(1, 6)
        ],
        [
            InlineKeyboardButton(text=str(i), callback_data=str(i))
            for i in range(6, 11)
        ],
    ],
)


def get_energy_directions_kb():
    kb = InlineKeyboardBuilder.from_markup(
        keyboard_from_choices(EnergyDirection),
    )
    kb.button(text='Выбрал', callback_data='done')
    return kb.adjust(1).as_markup()
