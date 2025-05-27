from datetime import datetime

from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message
from django.utils.timezone import now

from bot.config import config


def current_time():
    return now().astimezone(config.TZ).time()


async def validate_time(msg: Message):
    try:
        datetime.strptime(msg.text, '%H:%M')
        return msg.text
    except ValueError as e:
        await msg.answer('Ты ввёл некорректное время. Попробуй ещё раз.')
        raise SkipHandler from e
