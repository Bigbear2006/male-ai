import os

import django
from aiogram.types import BotCommand

from bot.loader import bot, dp, logger, loop


async def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from bot.handlers import (
        faq,
        habits,
        menu,
        profile,
        start,
        subscribe,
        survey,
        try_free_version,
    )

    dp.include_routers(
        start.router,
        menu.router,
        try_free_version.router,
        subscribe.router,
        survey.router,
        profile.router,
        habits.router,
        faq.router,
    )

    from bot.middlewares import WithClientMiddleware

    dp.message.middleware(WithClientMiddleware())
    dp.callback_query.middleware(WithClientMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='Запустить бота'),
        ],
    )

    logger.info('Starting bot...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop.run_until_complete(main())
