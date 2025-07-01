from datetime import datetime

from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from bot.config import config


async def validate_time(msg: Message):
    try:
        datetime.strptime(msg.text, config.TIME_FMT)
        return msg.text
    except ValueError as e:
        await msg.answer('Ты ввёл некорректное время. Попробуй ещё раз.')
        raise SkipHandler from e


async def validate_email(msg: Message):
    validator = EmailValidator()
    try:
        validator(msg.text)
        return msg.text
    except ValidationError as e:
        await msg.answer('Некорректная почта. Попробуй ещё раз.')
        raise SkipHandler from e
