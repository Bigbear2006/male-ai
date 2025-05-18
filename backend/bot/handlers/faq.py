from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.inline import back_to_start_kb

router = Router()


@router.callback_query(F.data == 'faq')
async def faq(query: CallbackQuery):
    await query.message.edit_text(
        'Ответы на часто задаваемые вопросы',
        reply_markup=back_to_start_kb,
    )
