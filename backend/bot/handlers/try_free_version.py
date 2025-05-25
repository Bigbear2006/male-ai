from aiogram import F, Router, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.inline import back_to_start_kb
from bot.keyboards.utils import keyboard_from_choices, one_button_keyboard
from core.choices import Priority, SpendTime
from core.models import Client

router = Router()


@router.callback_query(F.data == 'try_free_version')
@flags.with_client
async def try_free_version(query: CallbackQuery, client: Client):
    if client.free_survey_filled():
        await query.message.edit_text(
            'Ты уже заполнил данные.\n'
            'Я буду присылать тебе сообщения каждый день.',
            reply_markup=one_button_keyboard(
                text='SOS Кнопка',
                callback_data='sos_button',
                back_button_data='to_start',
            ),
        )
        return

    await query.message.edit_text(
        'Твой приоритет на сейчас',
        reply_markup=keyboard_from_choices(
            Priority,
            prefix='priority',
            back_button_data='to_start',
        ),
    )


@router.callback_query(F.data.startswith('priority'))
async def set_priority(query: CallbackQuery, state: FSMContext):
    await state.update_data(priority=query.data.split(':')[1])
    await query.message.edit_text(
        'Сколько времени в день ты готов себе уделять?',
        reply_markup=keyboard_from_choices(SpendTime, prefix='spend_time'),
    )


@router.callback_query(F.data.startswith('spend_time'))
async def set_spend_time(query: CallbackQuery, state: FSMContext):
    await Client.objects.update_by_id(
        query.message.chat.id,
        priority=await state.get_value('priority'),
        spend_time=query.data.split(':')[1],
    )
    await state.clear()
    await query.message.edit_text(
        'Записал!',
        reply_markup=back_to_start_kb,
    )
