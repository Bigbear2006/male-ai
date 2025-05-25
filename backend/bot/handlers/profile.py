from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import ai
from bot.keyboards.inline import menu_kb
from bot.keyboards.utils import keyboard_from_choices, one_button_keyboard
from bot.prompts import select_month_goal_prompt
from bot.states import ProfileState
from core.choices import UpgradeStyle
from core.models import Profile, Survey

router = Router()


@router.callback_query(
    F.data == 'entrust_ai',
    StateFilter(ProfileState.month_goal),
)
async def set_month_goal_with_ai(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        f'{query.message.text}\n\nВыбираю подходящую цель...',
    )
    survey = await Survey.objects.aget(pk=query.message.chat.id)
    month_goal = await ai.answer(select_month_goal_prompt(survey))
    await state.update_data(month_goal=month_goal)
    await query.message.edit_text(
        f'ИИ предлагает цель:\n{month_goal}\n\n'
        f'Ты можешь выбрать эту цель или написать свою.',
        reply_markup=one_button_keyboard(
            text='Выбрать эту цель',
            callback_data='set_month_goal',
        ),
    )


@router.message(F.text, StateFilter(ProfileState.month_goal))
@router.callback_query(
    F.data == 'set_month_goal',
    StateFilter(ProfileState.month_goal),
)
async def set_month_goal(msg: Message | CallbackQuery, state: FSMContext):
    if isinstance(msg, Message):
        answer_func = msg.answer
        month_goal = msg.text
    else:
        answer_func = msg.message.edit_text
        month_goal = await state.get_value('month_goal')

    await state.update_data(month_goal=month_goal)
    await state.set_state(ProfileState.growth_zones)
    await answer_func(
        text='Напиши 2-3 зоны роста - ключевые фокусы.',
        reply_markup=None,
    )


@router.message(F.text, StateFilter(ProfileState.growth_zones))
async def set_growth_zones(msg: Message, state: FSMContext):
    await state.update_data(growth_zones=msg.text)
    await state.set_state(ProfileState.upgrade_style)
    await msg.answer(
        'Выбери стиль прокачки',
        reply_markup=keyboard_from_choices(UpgradeStyle),
    )


@router.callback_query(StateFilter(ProfileState.upgrade_style))
async def set_upgrade_style(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await Profile.objects.acreate(
        client_id=query.message.chat.id,
        start_point=data['start_point'],
        month_goal=data['month_goal'],
        growth_zones=data['growth_zones'],
        upgrade_style=query.data,
    )
    await state.clear()
    await query.message.edit_text('Готово!', reply_markup=menu_kb)
