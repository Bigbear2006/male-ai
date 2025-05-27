from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import config
from bot.keyboards.utils import one_button_keyboard

start_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Попробовать бесплатную версию',
                callback_data='try_free_version',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Перейти на полный функционал',
                callback_data='buy_subscription',
            ),
        ],
        [
            InlineKeyboardButton(text='FAQ', callback_data='faq'),
            InlineKeyboardButton(
                text='Тех поддержка',
                url=config.SUPPORT_LINK,
            ),
        ],
    ],
)

back_to_start_kb = one_button_keyboard(text='Назад', callback_data='to_start')

menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Режим дня', callback_data='schedule')],
        [
            InlineKeyboardButton(
                text='Трекер привычек',
                callback_data='habits_menu',
            ),
        ],
        [InlineKeyboardButton(text='Челленджи', callback_data='challenges')],
        [
            InlineKeyboardButton(
                text='Микро-курсы / интенсивы',
                callback_data='courses',
            ),
        ],
        [InlineKeyboardButton(text='SOS Кнопка', callback_data='sos_button')],
    ],
)
