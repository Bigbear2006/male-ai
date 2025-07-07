from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.utils import one_button_keyboard


def get_settings_kb(*, cancel_subscription_button: bool):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='День еженедельного обзора',
                    callback_data='change_settings:week_report_day',
                ),
            ],
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
                InlineKeyboardButton(
                    text='Стиль прокачки',
                    callback_data='change_settings:upgrade_style',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Отменить подписку',
                    callback_data='cancel_subscription',
                ),
            ]
            if cancel_subscription_button
            else [],
            [InlineKeyboardButton(text='Назад', callback_data='to_start')],
        ],
    )


to_settings_kb = one_button_keyboard(text='Назад', callback_data='settings')

cancel_subscription_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Отменить подписку',
                callback_data='confirm_subscription_cancellation',
            ),
        ],
        [InlineKeyboardButton(text='Назад', callback_data='settings')],
    ],
)
