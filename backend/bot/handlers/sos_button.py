from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import ai
from bot.achievements import check_sos_button_usages
from bot.keyboards.start import back_to_start_kb
from bot.prompts import get_sos_help, select_overload_method
from bot.states import SosButtonState
from core.models import Client, ClientSosButtonUsage

router = Router()


@router.callback_query(F.data == 'sos_button')
async def sos_button(query: CallbackQuery, state: FSMContext):
    await state.set_state(SosButtonState.problem)
    await query.message.edit_text(
        'Если тебя что-то волнует - пиши, я помогу.',
        reply_markup=back_to_start_kb,
    )


@router.message(F.text, StateFilter(SosButtonState.problem))
@flags.with_client
async def resolve_sos_problem(msg: Message, state: FSMContext, client: Client):
    msg_to_edit = await msg.answer('Подбираю технику восстановления...')

    if not client.subscription_is_active():
        text = await ai.answer(await select_overload_method(msg.text))
        await msg_to_edit.edit_text(text, reply_markup=back_to_start_kb)
        await state.set_state()
        return

    messages = await state.get_value('messages')
    if not messages:
        messages = [
            {'role': 'system', 'content': await get_sos_help()},
        ]

    messages.append({'role': 'user', 'content': msg.text})
    text = await ai.chat(messages)
    messages.append({'role': 'assistant', 'content': text})

    if len(messages) < 7:
        await state.update_data(messages=messages)
        await msg_to_edit.edit_text(text)
        return

    await ClientSosButtonUsage.objects.acreate(client=client)
    await check_sos_button_usages(client.pk)

    await msg_to_edit.edit_text(text, reply_markup=back_to_start_kb)
    await state.clear()
