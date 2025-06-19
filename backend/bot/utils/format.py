from datetime import datetime, time

from django.utils.timezone import now

from bot.config import config


def time_to_str(__time: time):
    return __time.strftime(config.TIME_FMT)


def date_to_str(__date: datetime):
    return __date.astimezone(config.TZ).strftime(config.DATE_FMT)


def current_time():
    return now().astimezone(config.TZ).time()
