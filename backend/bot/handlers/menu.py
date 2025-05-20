from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.inline import menu_kb

router = Router()


@router.callback_query(F.data == 'to_menu')
async def to_menu(query: CallbackQuery):
    await query.message.edit_text('Главное меню', reply_markup=menu_kb)
