from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.config import config
from bot.keyboards.utils import one_button_keyboard

router = Router()


@router.callback_query(F.data == 'faq')
async def faq(query: CallbackQuery):
    await query.message.edit_text(
        'FAQ\n\n'
        '1. Как работает бот?\n'
        'Ты каждый день получаешь поддержку:\n'
        '— утром — фокус и настрой,\n'
        '— днём — напоминания и помощь,\n'
        '— вечером — рефлексию.\n'
        'Бот адаптируется под твой ритм и стиль.\n\n'
        '⸻\n\n'
        '2. Что делать, если я сбился с ритма?\n'
        'Ничего страшного. Просто нажми SOS-кнопку или напиши боту — '
        'он поможет восстановиться. Без упрёков. Без давления.\n\n'
        '⸻\n\n'
        '3. Как изменить стиль прокачки?\n'
        'Перейди в Настройки → Стиль прокачки.\n'
        'Доступны варианты: мягкий / жёсткий / адаптивный.\n\n'
        '⸻\n\n'
        '4. Как отключить или изменить подписку?\n'
        'Управление подпиской — через менеджера\n\n'
        '⸻\n\n'
        '5. Где задать вопрос или получить помощь?\n'
        'Нажми кнопку ниже — мы на связи.',
        reply_markup=one_button_keyboard(
            text='Менеджер',
            url=config.SUPPORT_LINK,
            back_button_data='to_start',
        ),
    )
