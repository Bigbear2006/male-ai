from datetime import datetime

from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message

from bot.config import config


async def validate_time(msg: Message):
    try:
        datetime.strptime(msg.text, config.TIME_FMT)
        return msg.text
    except ValueError as e:
        await msg.answer('Ты ввёл некорректное время. Попробуй ещё раз.')
        raise SkipHandler from e
