from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

wellbeing_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=str(i), callback_data=str(i))
            for i in range(1, 6)
        ],
    ],
)
