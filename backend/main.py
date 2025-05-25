import os

import django
from aiogram.types import BotCommand

from bot.loader import bot, dp, logger, loop


async def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from bot.handlers import (
        challenges,
        courses,
        daily_cycle,
        day_result,
        faq,
        habits,
        profile,
        sos_button,
        start,
        subscribe,
        survey,
        tests,
        try_free_version,
    )
    from bot.middlewares import WithClientMiddleware

    dp.include_routers(
        start.router,
        try_free_version.router,
        subscribe.router,
        survey.router,
        profile.router,
        daily_cycle.router,
        day_result.router,
        sos_button.router,
        habits.router,
        courses.router,
        challenges.router,
        faq.router,
        tests.router,
    )

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
