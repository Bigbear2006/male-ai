from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.utils import one_button_keyboard

settings_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Цель на месяц',
                callback_data='change_settings:month_goal',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Сферы прокачки',
                callback_data='change_settings:growth_zones',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Стиль прокачки',
                callback_data='change_settings:upgrade_style',
            ),
        ],
        [
            InlineKeyboardButton(
                text='День еженедельного обзора',
                callback_data='change_settings:week_report_day',
            ),
        ],
        [InlineKeyboardButton(text='Назад', callback_data='to_start')],
    ],
)

to_settings_kb = one_button_keyboard(text='Назад', callback_data='settings')
