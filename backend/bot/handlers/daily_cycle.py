from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.integrations.openai import openai_client
from bot.integrations.openai.prompts import (
    evening_support_prompt,
    morning_extended_message_prompt,
)
from bot.keyboards.daily_cycle import wellbeing_kb
from bot.services.achievement import (
    check_bot_usage,
    check_bot_usage_without_reset,
    check_daily_cycles_streak,
)
from bot.states import DailyCycleState
from core.choices import ManifestType
from core.models import Client, DailyCycle

router = Router()


@router.callback_query(F.data.startswith('manifest_type'))
@flags.with_client
async def set_manifest_type(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await query.message.edit_text('Подбираю микро цель...')
    manifest_type = ManifestType(query.data.split(':')[1])
    text = await openai_client.answer(
        await morning_extended_message_prompt(client, manifest_type),
    )

    await state.update_data(manifest_type=manifest_type.value)
    await state.set_state(DailyCycleState.morning_wellbeing)
    await query.message.edit_text(text)
    await query.message.answer(
        'Как твое самочувствие?',
        reply_markup=wellbeing_kb,
    )


@router.callback_query(DailyCycleState.morning_wellbeing)
async def set_wellbeing(query: CallbackQuery, state: FSMContext):
    await DailyCycle.objects.acreate(
        client_id=query.message.chat.id,
        manifest_type=await state.get_value('manifest_type'),
        morning_wellbeing=query.data,
    )
    await state.clear()
    await query.message.edit_text('Записал!')


@router.callback_query(F.data == 'set_success_result')
async def set_success_result(query: CallbackQuery, state: FSMContext):
    await state.set_state(DailyCycleState.success_result)
    await query.message.edit_text(
        f'{query.message.text}\nЖду твоего ответа...',
    )


@router.message(F.text, StateFilter(DailyCycleState.success_result))
async def set_success_result_2(msg: Message, state: FSMContext):
    await state.update_data(success_result=msg.text)
    await state.set_state(DailyCycleState.fail_result)
    await msg.answer('Что не получилось - и почему?')


@router.message(F.text, StateFilter(DailyCycleState.fail_result))
async def set_fail_result(msg: Message, state: FSMContext):
    await state.update_data(fail_result=msg.text)
    await state.set_state(DailyCycleState.feelings)
    await msg.answer('Как себя чувствовал сегодня?')


@router.message(F.text, StateFilter(DailyCycleState.feelings))
async def set_feelings(msg: Message, state: FSMContext):
    await state.update_data(feelings=msg.text)
    await state.set_state(DailyCycleState.evening_wellbeing)
    await msg.answer('Твоя самооценка', reply_markup=wellbeing_kb)


@router.callback_query(StateFilter(DailyCycleState.evening_wellbeing))
@flags.with_client
async def set_evening_wellbeing(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    data = await state.get_data()
    await DailyCycle.objects.create_or_update(
        query.message.chat.id,
        success_result=data['success_result'],
        fail_result=data['fail_result'],
        feelings=data['feelings'],
        evening_wellbeing=query.data,
    )

    await query.message.edit_text('Сохраняю данные...')
    text = await openai_client.answer(await evening_support_prompt(client))

    await check_daily_cycles_streak(client.pk)
    await check_bot_usage(client)
    await check_bot_usage_without_reset(client)

    await query.message.edit_text(text)
    await state.clear()
