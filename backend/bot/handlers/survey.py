import random

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import ai
from bot.greetings import greetings
from bot.keyboards.survey import (
    ages_kb,
    get_energy_directions_kb,
    self_ratings_kb,
)
from bot.keyboards.utils import keyboard_from_choices, one_button_keyboard
from bot.prompts import state_analysis_prompt
from bot.states import ProfileState, SurveyState
from core.choices import (
    EnergyDirection,
    Purpose,
    SupportOption,
    SupportStyle,
)
from core.models import Survey

router = Router()


@router.callback_query(F.data == 'to_survey')
async def survey_greeting(query: CallbackQuery):
    greeting = random.choice(greetings)
    await query.message.edit_text(**greeting)


@router.callback_query(F.data == 'start_survey')
async def start_survey(query: CallbackQuery, state: FSMContext):
    await state.set_state(SurveyState.preferred_name)
    await query.message.edit_text(
        'Как мне к тебе обращаться?',
        reply_markup=None,
    )


@router.message(F.text, StateFilter(SurveyState.preferred_name))
async def set_preferred_name(msg: Message, state: FSMContext):
    await state.update_data(preferred_name=msg.text)
    await state.set_state(SurveyState.age)
    await msg.answer(
        'Сколько тебе лет?\n\nВозраст поможет лучше настроить твой маршрут.',
        reply_markup=ages_kb,
    )


@router.message(F.text, StateFilter(SurveyState.age))
@router.callback_query(StateFilter(SurveyState.age))
async def set_age(msg: Message | CallbackQuery, state: FSMContext):
    if isinstance(msg, Message):
        answer_func = msg.answer
        try:
            age = int(msg.text)
        except ValueError:
            await msg.answer('Введи число или нажми одну из кнопок.')
            return
    else:
        answer_func = msg.message.edit_text
        age = msg.data

    await state.update_data(age=age)
    await state.set_state(SurveyState.shape)
    await answer_func(
        'Одним-двумя словами: какое у тебя внутреннее состояние сегодня?',
        reply_markup=None,
    )


@router.message(F.text, StateFilter(SurveyState.shape))
async def set_shape(msg: Message, state: FSMContext):
    await state.update_data(shape=msg.text)
    await state.set_state(SurveyState.last_forces_source)
    await msg.answer('Что последнее дало тебе силы или радость?')


@router.message(F.text, StateFilter(SurveyState.last_forces_source))
async def set_last_forces_source(msg: Message, state: FSMContext):
    await state.update_data(last_forces_source=msg.text)
    await state.set_state(SurveyState.self_rating)
    await msg.answer(
        'На шкале от 1 до 10 - насколько ты доволен собой сейчас?',
        reply_markup=self_ratings_kb,
    )


@router.callback_query(StateFilter(SurveyState.self_rating))
async def set_self_rating(query: CallbackQuery, state: FSMContext):
    await state.update_data(self_rating=query.data)
    await state.set_state(SurveyState.energy_directions)
    await query.message.edit_text(
        'Куда чаще всего уходит твоя энергия? Выбери до 2 вариантов.',
        reply_markup=get_energy_directions_kb(),
    )


@router.callback_query(StateFilter(SurveyState.energy_directions))
async def set_energy_direction(query: CallbackQuery, state: FSMContext):
    energy_directions = await state.get_value('energy_directions', [])

    if query.data != 'done':
        if query.data in energy_directions:
            energy_directions.remove(query.data)
        else:
            if len(energy_directions) >= 2:
                energy_directions[0] = query.data
            else:
                energy_directions.append(query.data)

        await state.update_data(energy_directions=energy_directions)
        energy_directions_str = ', '.join(
            [str(EnergyDirection(i).label) for i in energy_directions],
        )
        await query.message.edit_text(
            'Куда чаще всего уходит твоя энергия? Выбери до 2 вариантов.\n\n'
            f'Ты выбрал: {energy_directions_str}',
            reply_markup=get_energy_directions_kb(),
        )
        return

    if len(energy_directions) == 0:
        try:
            await query.message.edit_text(
                'Куда чаще всего уходит твоя энергия?\n\n'
                'Надо выбрать минимум 1 вариант.',
                reply_markup=get_energy_directions_kb(),
            )
        except TelegramBadRequest:
            pass
        return

    await state.set_state(SurveyState.purpose)
    await query.message.edit_text(
        'Что тебе сейчас важнее всего?',
        reply_markup=keyboard_from_choices(Purpose),
    )


@router.callback_query(StateFilter(SurveyState.purpose))
async def set_purpose(query: CallbackQuery, state: FSMContext):
    await state.update_data(purpose=query.data)
    await state.set_state(SurveyState.future_version)
    await query.message.edit_text(
        'Чего хочешь достигнуть через 30 дней? Опиши в 1-2 фразах.',
        reply_markup=None,
    )


@router.message(F.text, StateFilter(SurveyState.future_version))
async def set_future_version(msg: Message, state: FSMContext):
    await state.update_data(future_version=msg.text)
    await state.set_state(SurveyState.support_style)
    await msg.answer(
        'Какой стиль поддержки тебе ближе?',
        reply_markup=keyboard_from_choices(SupportStyle),
    )


@router.callback_query(StateFilter(SurveyState.support_style))
async def set_support_style(query: CallbackQuery, state: FSMContext):
    await state.update_data(support_style=query.data)
    await state.set_state(SurveyState.support_option)
    await query.message.edit_text(
        'Когда что-то идёт не так - что тебе больше всего помогает?',
        reply_markup=keyboard_from_choices(SupportOption),
    )


@router.callback_query(StateFilter(SurveyState.support_option))
async def set_support_option(query: CallbackQuery, state: FSMContext):
    await state.update_data(support_option=query.data)
    await state.set_state(SurveyState.key_quality)
    await query.message.edit_text(
        'Одним словом: какое качество тебе сейчас хочется усилить',
        reply_markup=None,
    )


@router.message(F.text, StateFilter(SurveyState.key_quality))
async def set_key_quality(msg: Message, state: FSMContext):
    data = await state.get_data()
    survey = await Survey.objects.create_or_update(
        msg.chat.id,
        preferred_name=data['preferred_name'],
        age=data['age'],
        shape=data['shape'],
        last_forces_source=data['last_forces_source'],
        self_rating=data['self_rating'],
        energy_directions=data['energy_directions'],
        purpose=data['purpose'],
        future_version=data['future_version'],
        support_style=data['support_style'],
        support_option=data['support_option'],
        key_quality=msg.text,
    )

    msg_to_edit = await msg.answer('Составляю твой профиль 1.0...')
    start_point = await ai.answer(state_analysis_prompt(survey))
    await state.set_data({'start_point': start_point})
    await state.set_state(ProfileState.month_goal)
    await msg_to_edit.edit_text(
        'Твой профиль 1.0 готов!\n\n'
        f'Вот твоя точка старта:\n{start_point}\n\n'
        'Напиши свою цель на следующие 30 дней.',
        reply_markup=one_button_keyboard(
            text='Доверить выбор цели ИИ',
            callback_data='entrust_ai',
        ),
    )
