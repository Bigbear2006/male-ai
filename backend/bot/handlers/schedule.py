from aiogram import F, Router, flags
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.schedule import (
    get_edit_time_block_kb,
    get_time_block_kb,
    schedule_kb,
)
from bot.keyboards.utils import (
    keyboard_from_choices,
    keyboard_from_queryset,
    one_button_keyboard,
)
from bot.states import ScheduleState
from bot.utils.validation import validate_time
from core.choices import ScheduleType
from core.models import Schedule, TimeBlock

router = Router()


@router.callback_query(F.data == 'schedule')
@flags.with_client(only_subscribers=True)
async def schedule_handler(query: CallbackQuery, state: FSMContext):
    await state.set_state()

    schedule = await Schedule.objects.get_by_id(pk=query.message.chat.id)
    if not schedule:
        await query.message.edit_text(
            'Ты ещё не настраивал режим дня',
            reply_markup=one_button_keyboard(
                text='Настроить',
                callback_data='set_schedule_type',
            ),
        )
        return

    await query.message.edit_text(
        schedule.message_text,
        reply_markup=schedule_kb,
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == 'set_schedule_type')
async def choose_schedule_type(query: CallbackQuery):
    await query.message.edit_text(
        'Выбери режим дня',
        reply_markup=keyboard_from_choices(
            ScheduleType,
            prefix='schedule_type',
            back_button_data='schedule',
        ),
    )


@router.callback_query(F.data.startswith('schedule_type'))
async def set_schedule_type(query: CallbackQuery):
    client_id = query.message.chat.id
    schedule_type = ScheduleType(query.data.split(':')[1])
    await Schedule.objects.create_or_update(client_id, schedule_type)

    try:
        await query.message.edit_text(
            f'Выбери режим дня\nТекущий режим: {schedule_type.label}',
            reply_markup=keyboard_from_choices(
                ScheduleType,
                prefix='schedule_type',
                back_button_data='schedule',
            ),
        )
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == 'time_blocks')
async def time_blocks(query: CallbackQuery):
    await query.message.edit_text(
        'Твои блоки',
        reply_markup=await keyboard_from_queryset(
            TimeBlock.objects.filter(schedule_id=query.message.chat.id),
            prefix='time_block',
            back_button_data='schedule',
        ),
    )


@router.callback_query(F.data.startswith('time_block'))
async def time_block_detail(query: CallbackQuery):
    time_block = await TimeBlock.objects.aget(pk=query.data.split(':')[1])
    await query.message.edit_text(
        time_block.message_text,
        reply_markup=get_time_block_kb(time_block.pk),
    )


@router.callback_query(F.data.startswith('edit_time_block'))
async def edit_time_block(query: CallbackQuery):
    await query.message.edit_text(
        'Выбери, что хочешь изменить',
        reply_markup=get_edit_time_block_kb(query.data.split(':')[1]),
    )


@router.callback_query(F.data.startswith('tb_field'))
async def edit_time_block_field(query: CallbackQuery, state: FSMContext):
    _, field, pk = query.data.split(':')
    texts = {
        'name': 'Введи название блока',
        'start_time': 'Укажи время начала блока в формате ЧЧ:ММ',
        'end_time': 'Укажи время завершения блока в формате ЧЧ:ММ',
    }

    await state.update_data(field=field, time_block_id=pk)
    await state.set_state(ScheduleState.time_block_edit)
    await query.message.edit_text(
        texts[field],
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data=f'edit_time_block:{pk}',
        ),
    )


@router.message(F.text, StateFilter(ScheduleState.time_block_edit))
async def edit_time_block_field_2(msg: Message, state: FSMContext):
    data = await state.get_data()
    pk = data['time_block_id']
    field = data['field']

    if field != 'name':
        await validate_time(msg)

    await TimeBlock.objects.filter(pk=pk).aupdate(**{field: msg.text})
    await state.clear()
    await msg.answer(
        'Блок изменён!',
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data=f'edit_time_block:{pk}',
        ),
    )


@router.callback_query(F.data.startswith('delete_time_block'))
async def delete_time_block(query: CallbackQuery):
    await TimeBlock.objects.filter(pk=query.data.split(':')[1]).adelete()
    await query.message.edit_text(
        'Твои блоки',
        reply_markup=await keyboard_from_queryset(
            TimeBlock.objects.filter(schedule_id=query.message.chat.id),
            prefix='time_block',
            back_button_data='schedule',
        ),
    )


@router.callback_query(F.data == 'add_time_block')
async def add_time_block(query: CallbackQuery, state: FSMContext):
    await state.set_state(ScheduleState.time_block_name)
    await query.message.edit_text(
        'Введи название блока',
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data='schedule',
        ),
    )


@router.message(F.text, StateFilter(ScheduleState.time_block_name))
async def set_time_block_name(msg: Message, state: FSMContext):
    await state.update_data(time_block_name=msg.text)
    await state.set_state(ScheduleState.time_block_start)
    await msg.answer('Укажи время начала блока в формате ЧЧ:ММ')


@router.message(F.text, StateFilter(ScheduleState.time_block_start))
async def set_time_block_start(msg: Message, state: FSMContext):
    await validate_time(msg)
    await state.update_data(time_block_start=msg.text)
    await state.set_state(ScheduleState.time_block_end)
    await msg.answer(
        'Укажи время завершения блока в формате ЧЧ:ММ',
        reply_markup=one_button_keyboard(
            text='Не указывать',
            callback_data='skip_time_block_end',
        ),
    )


@router.message(F.text, StateFilter(ScheduleState.time_block_end))
async def set_time_block_end(msg: Message, state: FSMContext):
    await validate_time(msg)
    data = await state.get_data()
    await TimeBlock.objects.acreate(
        schedule_id=msg.chat.id,
        name=data['time_block_name'],
        start_time=data['time_block_start'],
        end_time=msg.text,
    )

    await state.clear()
    await msg.answer(
        'Блок добавлен!',
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data='time_blocks',
        ),
    )


@router.callback_query(F.data == 'skip_time_block_end')
async def skip_time_block_end(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await TimeBlock.objects.acreate(
        schedule_id=query.message.chat.id,
        name=data['time_block_name'],
        start_time=data['time_block_start'],
    )

    await state.clear()
    await query.message.edit_text(
        'Блок добавлен!',
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data='time_blocks',
        ),
    )
