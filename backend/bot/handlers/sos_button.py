from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import ai
from bot.keyboards.inline import back_to_start_kb
from bot.prompts import select_overload_method
from bot.states import SosButtonState

router = Router()


@router.callback_query(F.data == 'sos_button')
async def sos_button(query: CallbackQuery, state: FSMContext):
    await state.set_state(SosButtonState.problem)
    await query.message.edit_text(
        'Если тебя что-то волнует - пиши, я помогу.',
        reply_markup=back_to_start_kb,
    )


@router.message(F.text, StateFilter(SosButtonState.problem))
async def resolve_sos_problem(msg: Message, state: FSMContext):
    msg_to_edit = await msg.answer('Подбираю технику восстановления...')
    text = await ai.answer(select_overload_method(msg.text))
    await msg_to_edit.edit_text(text, reply_markup=back_to_start_kb)
    await state.set_state(None)
