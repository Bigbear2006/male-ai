from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.integrations.openai import openai_client
from bot.integrations.openai.prompts import (
    get_sos_help,
    select_overload_method,
)
from bot.keyboards.start import back_to_start_kb
from bot.services.achievement import check_sos_button_usages
from bot.states import SosButtonState
from core.models import Client, ClientSosButtonUsage

router = Router()


@router.callback_query(F.data == 'sos_button')
async def sos_button(query: CallbackQuery, state: FSMContext):
    await state.set_state(SosButtonState.problem)
    await query.message.edit_text(
        '⚡️ SOS Кнопка\n\n'
        'Когда не держишь ритм. Или накрывает.\n\n'
        'Если тяжело — нажми. Здесь ты получишь поддержку: словами, вопросом, направлением.\n'
        'Без шаблонов. Без поверхностных советов. Только по сути — как разговор с тем, кто понимает.\n\n'
        '✏️ Просто напиши сюда, что тебя тревожит — и мы начнём.\n',
        reply_markup=back_to_start_kb,
    )


@router.message(F.text, StateFilter(SosButtonState.problem))
@flags.with_client
async def resolve_sos_problem(msg: Message, state: FSMContext, client: Client):
    msg_to_edit = await msg.answer('Печатает...')

    if not await client.subscription_is_active():
        text = await openai_client.answer(
            await select_overload_method(msg.text),
        )
        await msg_to_edit.edit_text(text, reply_markup=back_to_start_kb)
        await state.set_state()
        return

    messages = await state.get_value('messages')
    if not messages:
        messages = [
            {'role': 'system', 'content': await get_sos_help()},
        ]

    messages.append({'role': 'user', 'content': msg.text})
    text = await openai_client.chat(messages)
    messages.append({'role': 'assistant', 'content': text})

    if len(messages) < 7:
        await state.update_data(messages=messages)
        await msg_to_edit.edit_text(text)
        return

    await msg_to_edit.edit_text(text, reply_markup=back_to_start_kb)
    await state.clear()

    await ClientSosButtonUsage.objects.acreate(client=client)
    await check_sos_button_usages(client.pk)
