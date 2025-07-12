from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.keyboards.start import start_kb
from bot.utils.greetings import start_short_msg_text
from core.models import Client


class WithClientMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        with_client = get_flag(data, 'with_client')
        if with_client:
            pk = (
                event.chat.id
                if isinstance(event, Message)
                else event.message.chat.id
            )

            select_related = ()
            only_subscribers = False
            if isinstance(with_client, dict):
                select_related = with_client.get(
                    'select_related',
                    ('start_promo_code',),
                )
                only_subscribers = with_client.get('only_subscribers', False)

            client = await Client.objects.select_related(
                *select_related,
            ).aget(pk=pk)

            if only_subscribers and not await client.subscription_is_active():
                answer_func = (
                    event.answer
                    if isinstance(event, Message)
                    else event.message.answer
                )
                await answer_func(start_short_msg_text, reply_markup=start_kb)
                raise SkipHandler

            data['client'] = client
        return await handler(event, data)
