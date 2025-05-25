from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.utils import get_courses_kb

router = Router()


@router.callback_query(F.data == 'courses')
async def courses(query: CallbackQuery):
    await query.message.edit_text(
        'Микро курсы / интенсивы',
        reply_markup=await get_courses_kb(),
    )
