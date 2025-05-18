import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from bot.config import config

logger = logging.getLogger('bot')
loop = asyncio.get_event_loop()

bot = Bot(config.BOT_TOKEN)
storage = RedisStorage.from_url(config.REDIS_URL)
dp = Dispatcher(storage=storage)
