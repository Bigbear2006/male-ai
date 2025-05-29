import asyncio
import functools

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.utils.timezone import now

from bot import ai
from bot.keyboards.utils import keyboard_from_choices, one_button_keyboard
from bot.loader import bot
from bot.prompts import day_message_prompt, morning_message_prompt
from bot.time_utils import current_time
from core.choices import ManifestType
from core.models import (
    ChallengeTask,
    Client,
    ClientChallenge,
    ClientChallengeTaskQuestion,
    TimeBlock,
)

task_logger = get_task_logger(__name__)


def handle_send_message_errors(send_message_func):
    async def decorator(chat_id: int | str, text: str, **kwargs):
        try:
            await send_message_func(chat_id, text, **kwargs)
        except TelegramRetryAfter as e:
            task_logger.info(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of rate limit',
            )
            await asyncio.sleep(e.retry_after)
            await send_message_func(chat_id, text, **kwargs)
        except TelegramBadRequest as e:
            task_logger.info(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of an {e.__class__.__name__} error: {str(e)}',
            )

    return decorator


@handle_send_message_errors
async def safe_send_message(chat_id: int | str, text: str, **kwargs):
    return await bot.send_message(chat_id, text, **kwargs)


def async_shared_task(func):
    @shared_task
    @functools.wraps(func)
    def decorator():
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        loop.run_until_complete(func())

    return decorator


async def asyncio_wait(
    fs,
    *,
    timeout=None,
    return_when=asyncio.ALL_COMPLETED,
) -> tuple[set, set]:
    if not fs:
        return set(), set()
    return await asyncio.wait(fs, timeout=timeout, return_when=return_when)


async def send_free_morning_message(client: Client):
    text = await ai.answer(await morning_message_prompt(client))
    await safe_send_message(client.pk, text)


@async_shared_task
async def send_free_morning_messages():
    await asyncio_wait(
        [
            asyncio.create_task(send_free_morning_message(c))
            async for c in Client.objects.get_unsubscribed(
                exclude_survey_unfilled=True,
            )
        ],
    )


@async_shared_task
async def send_free_evening_messages():
    text = 'Что сегодня получилось лучше, чем вчера?'
    kb = one_button_keyboard(text='Ответить', callback_data='set_day_result')
    await asyncio_wait(
        [
            asyncio.create_task(safe_send_message(c.pk, text, reply_markup=kb))
            async for c in Client.objects.get_unsubscribed(
                exclude_survey_unfilled=True,
            )
        ],
    )


@async_shared_task
async def send_subscription_notifications():
    text = (
        'Хочешь выстроить дисциплину глубже? '
        'В полной версии - трекеры, режим дня, челленджи и личный прогресс.'
    )
    kb = one_button_keyboard(
        text='Купить подписку',
        callback_data='buy_subscription',
    )
    await asyncio_wait(
        [
            asyncio.create_task(safe_send_message(c.pk, text, reply_markup=kb))
            async for c in Client.objects.get_unsubscribed()
        ],
    )


@async_shared_task
async def send_morning_messages():
    text = 'Как ты хочешь проявиться сегодня?'
    kb = keyboard_from_choices(ManifestType, prefix='manifest_type')
    await asyncio_wait(
        [
            asyncio.create_task(safe_send_message(c.pk, text, reply_markup=kb))
            async for c in Client.objects.get_subscribed(
                exclude_survey_unfilled=True,
            )
        ],
    )


async def send_day_message(client_id: int | str):
    text = await ai.answer(await day_message_prompt(client_id))
    await safe_send_message(client_id, text)


@async_shared_task
async def send_day_messages():
    hour = current_time().hour
    await asyncio_wait(
        [
            asyncio.create_task(send_day_message(c))
            async for c in TimeBlock.objects.filter(
                start_time__hour=hour,
                schedule__client__subscription_end__gte=now(),
                schedule__client__survey__isnull=False,
                schedule__client__profile__isnull=False,
            )
            .values_list('schedule__client', flat=True)
            .order_by()
            .distinct()
        ],
    )


@async_shared_task
async def send_evening_messages():
    text = 'Что удалось сегодня?'
    kb = one_button_keyboard(
        text='Ответить',
        callback_data='set_success_result',
    )
    await asyncio_wait(
        [
            asyncio.create_task(safe_send_message(c.pk, text, reply_markup=kb))
            async for c in Client.objects.get_subscribed(
                exclude_survey_unfilled=True,
            )
        ],
    )


async def send_challenge_task(client_challenge: ClientChallenge):
    last_day = (
        await ClientChallengeTaskQuestion.objects.get_last_completed_day(
            client_challenge.client_id,
            client_challenge.challenge_id,
        )
    )

    try:
        task = await ChallengeTask.objects.select_related('challenge').aget(
            challenge_id=client_challenge.challenge_id,
            day=last_day + 1,
        )
    except ObjectDoesNotExist:
        return

    await safe_send_message(client_challenge.client_id, task.message_text)


@async_shared_task
async def send_challenge_tasks():
    await asyncio_wait(
        [
            asyncio.create_task(send_challenge_task(c))
            async for c in ClientChallenge.objects.all()
        ],
    )


async def send_challenge_task_questions(client_challenge: ClientChallenge):
    last_day = (
        await ClientChallengeTaskQuestion.objects.get_last_completed_day(
            client_challenge.client_id,
            client_challenge.challenge_id,
        )
    )

    try:
        task = await ChallengeTask.objects.prefetch_related('questions').aget(
            challenge_id=client_challenge.challenge_id,
            day=last_day + 1,
        )
    except ObjectDoesNotExist:
        return

    if not task.questions:
        return

    await safe_send_message(
        client_challenge.client_id,
        'Как ты справился с сегодняшним заданием?',
        reply_markup=one_button_keyboard(
            text='Ответить на вопросы',
            callback_data=f'answer_challenge_task_questions:{task.pk}',
        ),
    )


@async_shared_task
async def send_challenge_tasks_questions():
    await asyncio_wait(
        [
            asyncio.create_task(send_challenge_task_questions(c))
            async for c in ClientChallenge.objects.all()
        ],
    )
