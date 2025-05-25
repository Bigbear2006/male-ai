from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async
from django.db import IntegrityError

from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from bot.states import ChallengeState
from core.models import (
    Challenge,
    ChallengeTaskQuestion,
    ClientChallenge,
    ClientChallengeTaskQuestion,
)

router = Router()


@router.callback_query(F.data == 'challenges')
async def challenges(query: CallbackQuery):
    await query.message.edit_text(
        'Челленджи',
        reply_markup=await keyboard_from_queryset(
            Challenge.objects.all(),
            prefix='challenge',
            back_button_data='to_start',
        ),
    )


@router.callback_query(F.data.startswith('challenge'))
async def challenge_detail(query: CallbackQuery):
    challenge = await Challenge.objects.aget(pk=query.data.split(':')[1])
    await query.message.edit_text(
        challenge.message_text,
        reply_markup=one_button_keyboard(
            text='Участвовать',
            callback_data=f'join_challenge:{challenge.pk}',
            back_button_data='challenges',
        ),
    )


@router.callback_query(F.data.startswith('join_challenge'))
async def join_challenge(query: CallbackQuery):
    try:
        await ClientChallenge.objects.acreate(
            client_id=query.message.chat.id,
            challenge_id=query.data.split(':')[1],
        )
    except IntegrityError:
        await query.message.reply('Ты уже участвуешь в этом челлендже')
        return

    await query.message.reply('Теперь ты участвуешь в этом челлендже')


@router.callback_query(F.data.startswith('answer_challenge_task_questions'))
async def answer_challenge_task_first_question(
    query: CallbackQuery,
    state: FSMContext,
):
    questions = await sync_to_async(
        lambda: list(
            ChallengeTaskQuestion.objects.filter(
                task_id=query.data.split(':')[1],
            ).values('id', 'title'),
        ),
    )()

    await state.update_data(questions=questions, question_index=0)
    await state.set_state(ChallengeState.answer_task_questions)
    await query.message.edit_text(questions[0]['title'])


@router.message(F.text, StateFilter(ChallengeState.answer_task_questions))
async def answer_challenge_task_question(msg: Message, state: FSMContext):
    data = await state.get_data()
    questions = data['questions']
    index = data['question_index']

    await ClientChallengeTaskQuestion.objects.acreate(
        client_id=msg.chat.id,
        question_id=questions[index]['id'],
        answer=msg.text,
    )

    if len(questions) > index + 1:
        await state.update_data(question_index=index + 1)
        await msg.answer(questions[index + 1]['title'])
        return

    await state.clear()
    await msg.answer('Все ответы записаны!')
