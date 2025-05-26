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

wellbeing_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=str(i), callback_data=str(i))
            for i in range(1, 6)
        ],
    ],
)

schedule_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Режим дня',
                callback_data='set_schedule_type',
            ),
        ],
        [InlineKeyboardButton(text='Блоки', callback_data='time_blocks')],
        [
            InlineKeyboardButton(
                text='Добавить блок',
                callback_data='add_time_block',
            ),
        ],
        [InlineKeyboardButton(text='Назад', callback_data='to_start')],
    ],
)


def get_time_block_kb(time_block_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Редактировать',
                    callback_data=f'edit_time_block:{time_block_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Удалить',
                    callback_data=f'delete_time_block:{time_block_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data=f'time_blocks',
                ),
            ],
        ],
    )


def get_edit_time_block_kb(time_block_id: int | str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Название',
                    callback_data=f'tb_field:name:{time_block_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Дата начала',
                    callback_data=f'tb_field:start_time:{time_block_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Дата завершения',
                    callback_data=f'tb_field:end_time:{time_block_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data=f'time_block:{time_block_id}',
                ),
            ],
        ],
    )
