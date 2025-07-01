from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.utils import one_button_keyboard

subscribe_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Оплатить',
                callback_data='pay_subscription',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Активировать промокод',
                callback_data='activate_promo_code',
            ),
        ],
        [InlineKeyboardButton(text='Назад', callback_data='to_start')],
    ],
)

to_subscribe_kb = one_button_keyboard(
    text='Назад',
    callback_data='buy_subscription',
)

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
