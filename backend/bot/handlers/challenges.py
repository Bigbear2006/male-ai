from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.utils.timezone import now

from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from bot.services.achievement import (
    check_challenge_tasks_streak,
    check_completed_challenges,
    check_started_challenges,
)
from bot.states import ChallengeState
from core.models import (
    Challenge,
    ChallengeTask,
    ChallengeTaskQuestion,
    ClientChallenge,
    ClientChallengeTaskQuestion,
)

router = Router()


@router.callback_query(F.data == 'challenges')
@flags.with_client(only_subscribers=True)
async def challenges(query: CallbackQuery):
    await query.message.edit_text(
        '🧩 Челленджи\n\n'
        'Короткие задачи на 3–7 дней, чтобы укрепиться в конкретной зоне.\n'
        'Ты выбираешь направление — система помогает '
        'удержаться и завершить.\n',
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
    kb = one_button_keyboard(text='Назад', callback_data='challenges')
    try:
        await ClientChallenge.objects.acreate(
            client_id=query.message.chat.id,
            challenge_id=query.data.split(':')[1],
        )
        await check_started_challenges(query.message.chat.id)
    except IntegrityError:
        await query.message.reply(
            'Ты уже участвуешь в этом челлендже',
            reply_markup=kb,
        )
        return

    await query.message.reply(
        'Теперь ты участвуешь в этом челлендже',
        reply_markup=kb,
    )


@router.callback_query(F.data.startswith('answer_challenge_task_questions'))
async def answer_challenge_task_first_question(
    query: CallbackQuery,
    state: FSMContext,
):
    task_id = query.data.split(':')[1]
    questions = await sync_to_async(
        lambda: list(
            ChallengeTaskQuestion.objects.filter(task_id=task_id).values(
                'id',
                'title',
            ),
        ),
    )()

    await state.update_data(
        questions=questions,
        question_index=0,
        task_id=task_id,
    )
    await state.set_state(ChallengeState.answer_task_questions)
    await query.message.edit_text(questions[0]['title'])


@router.message(F.text, StateFilter(ChallengeState.answer_task_questions))
async def answer_challenge_task_question(msg: Message, state: FSMContext):
    data = await state.get_data()
    questions = data['questions']
    index = data['question_index']

    await ClientChallengeTaskQuestion.objects.create_or_update(
        msg.chat.id,
        question_id=questions[index]['id'],
        answer=msg.text,
    )

    if len(questions) > index + 1:
        await state.update_data(question_index=index + 1)
        await msg.answer(questions[index + 1]['title'])
        return

    challenge_id = (
        await ChallengeTask.objects.aget(pk=data['task_id'])
    ).challenge_id

    await ClientChallenge.objects.filter(
        client_id=msg.chat.id,
        challenge_id=challenge_id,
    ).aupdate(completed_at=now())

    await check_completed_challenges(msg.chat.id)
    await check_challenge_tasks_streak(msg.chat.id)

    await msg.answer('Все ответы записаны!')
    await state.clear()
