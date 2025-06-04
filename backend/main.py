import os

import django
from aiogram import F
from aiogram.enums import ChatType
from aiogram.types import BotCommand

from bot.loader import bot, dp, logger, loop


async def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from bot.handlers import (
        achievements,
        challenges,
        courses,
        daily_cycle,
        day_result,
        faq,
        habits,
        profile,
        schedule,
        settings,
        sos_button,
        start,
        subscribe,
        survey,
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
        schedule.router,
        achievements.router,
        settings.router,
        faq.router,
    )

    dp.message.middleware(WithClientMiddleware())
    dp.callback_query.middleware(WithClientMiddleware())

    dp.message.filter(F.chat.type == ChatType.PRIVATE)
    dp.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='Запустить бота'),
            BotCommand(command='/menu', description='Главное меню'),
        ],
    )

    logger.info('Starting bot...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop.run_until_complete(main())
