from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.models import Course


async def get_courses_kb():
    kb = InlineKeyboardBuilder()
    async for course in Course.objects.all():
        kb.button(text=str(course), url=f'{course.url}')
    kb.button(text='Назад', callback_data='to_start')
    return kb.adjust(1).as_markup()
