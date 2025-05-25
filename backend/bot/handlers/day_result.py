from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.states import DayResultState
from core.models import DayResult

router = Router()


@router.callback_query(F.data == 'set_day_result')
async def set_day_result(query: CallbackQuery, state: FSMContext):
    await state.set_state(DayResultState.result)
    await query.message.edit_text(
        f'{query.message.text}\nЖду твоего ответа...',
    )


@router.message(F.text, StateFilter(DayResultState.result))
async def set_day_result_2(msg: Message, state: FSMContext):
    await DayResult.objects.acreate(
        client_id=msg.chat.id,
        result=msg.text[:255],
    )
    await state.set_state(None)
    await msg.answer('Записал!')
