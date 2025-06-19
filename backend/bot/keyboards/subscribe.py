from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

pay_subscription_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Я оплатил',
                callback_data='check_subscription_buying',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_subscription_buying',
            ),
        ],
    ],
)
