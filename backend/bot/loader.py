import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from openai import AsyncOpenAI

from bot.config import config

logger = logging.getLogger('bot')
loop = asyncio.get_event_loop()
openai_client = AsyncOpenAI(base_url='https://api.proxyapi.ru/openai/v1')

bot = Bot(config.BOT_TOKEN)
storage = RedisStorage.from_url(config.REDIS_URL)
dp = Dispatcher(storage=storage)
