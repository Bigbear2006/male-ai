from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.courses import get_courses_kb

router = Router()


@router.callback_query(F.data == 'courses')
async def courses(query: CallbackQuery):
    await query.message.edit_text(
        '📚 Микро-курсы / интенсивы\n\n'
        'Формат для прокачки ключевых навыков через действие.\n'
        'Короткие модули, пошаговая практика и ежедневная поддержка.\n',
        reply_markup=await get_courses_kb(),
    )
