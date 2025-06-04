from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.habits import get_habit_kb, get_habits_kb, habits_menu_kb
from bot.keyboards.utils import one_button_keyboard
from bot.states import HabitState
from core.models import Habit

router = Router()

habits_msg = (
    '✅ Трекер привычек\n\n'
    'То, что хочешь внедрить — фиксируешь и сверяешь каждый вечер.\n'
    'Добавляешь привычки, отмечаешь выполнение, видишь прогресс.\n'
)


@router.callback_query(F.data == 'habits_menu')
async def habits_menu(query: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await query.message.edit_text(
        habits_msg,
        reply_markup=habits_menu_kb,
    )


@router.callback_query(F.data == 'habits')
async def habits_list(query: CallbackQuery, state: FSMContext):
    await state.update_data(page=1)
    await query.message.edit_text(
        habits_msg,
        reply_markup=await get_habits_kb(query.message.chat.id, page=1),
    )


@router.callback_query(F.data.in_(('habits_previous', 'habits_next')))
async def change_habits_page(query: CallbackQuery, state: FSMContext):
    page = await state.get_value('page')
    if query.data == 'habits_previous':
        page -= 1
    else:
        page += 1
    await state.update_data(page=page)
    await query.message.edit_text(
        habits_msg,
        reply_markup=await get_habits_kb(query.message.chat.id, page=page),
    )


@router.callback_query(F.data.startswith('habit'))
async def habit_detail(query: CallbackQuery, state: FSMContext):
    habit = await Habit.objects.aget(pk=query.data.split(':')[1])
    await state.set_state(None)
    await query.message.edit_text(
        f'Привычка {habit.name}',
        reply_markup=get_habit_kb(habit.pk),
    )


@router.callback_query(F.data.startswith('add_habit'))
async def add_habit(query: CallbackQuery, state: FSMContext):
    await state.set_state(HabitState.add)
    await query.message.edit_text(
        'Введи название привычки',
        reply_markup=one_button_keyboard(
            text='Отмена',
            callback_data='habits_menu',
        ),
    )


@router.message(F.text, StateFilter(HabitState.add))
async def add_habit_2(msg: Message, state: FSMContext):
    await Habit.objects.acreate(
        client_id=msg.chat.id,
        name=msg.text,
    )
    await state.set_state(None)
    await msg.answer(
        f'Привычка {msg.text} добавлена',
        reply_markup=one_button_keyboard(
            text='Все привычки',
            callback_data='habits',
        ),
    )


@router.callback_query(F.data.startswith('update_habit'))
async def update_habit(query: CallbackQuery, state: FSMContext):
    habit_id = query.data.split(':')[1]
    await state.update_data(habit_id=habit_id)
    await state.set_state(HabitState.update)
    await query.message.edit_text(
        'Введите название привычки',
        reply_markup=one_button_keyboard(
            text='Отмена',
            callback_data=f'habit:{habit_id}',
        ),
    )


@router.message(F.text, StateFilter(HabitState.update))
async def update_habit_2(msg: Message, state: FSMContext):
    habit_id = await state.get_value('habit_id')
    await Habit.objects.filter(pk=habit_id).aupdate(
        name=msg.text,
    )
    await state.set_state(None)
    await msg.answer(
        'Привычка изменена!',
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data=f'habit:{habit_id}',
        ),
    )


@router.callback_query(F.data.startswith('delete_habit'))
async def delete_habit(query: CallbackQuery, state: FSMContext):
    habit_id = query.data.split(':')[1]
    page = await state.get_value('page', 1)
    await Habit.objects.filter(pk=habit_id).adelete()
    await query.message.edit_text(
        habits_msg,
        reply_markup=await get_habits_kb(query.message.chat.id, page=page),
    )
