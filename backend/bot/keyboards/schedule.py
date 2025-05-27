from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
                    callback_data='time_blocks',
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
