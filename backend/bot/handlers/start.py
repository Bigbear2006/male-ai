from aiogram import F, Router, flags
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.common.greetings import start_msg_text, start_short_msg_text
from bot.keyboards.start import menu_kb, start_kb
from bot.keyboards.utils import one_button_keyboard
from bot.loader import logger
from core.models import Client

router = Router()


@router.message(Command('start', 'menu'))
async def start(msg: Message, state: FSMContext):
    await state.set_state()

    client, created = await Client.objects.create_or_update(msg.from_user)
    if created:
        logger.info(f'New client {client} id={client.pk} was created')
    else:
        logger.info(f'Client {client} id={client.pk} was updated')

    if client.subscription_is_active():
        if not await client.has_profile():
            await msg.answer(
                start_msg_text,
                reply_markup=one_button_keyboard(
                    text='Пройти анкетирование',
                    callback_data='to_survey',
                ),
            )
            return

        await msg.answer(start_short_msg_text, reply_markup=menu_kb)
        return

    await msg.answer(start_msg_text, reply_markup=start_kb)


@router.callback_query(F.data == 'to_start')
@flags.with_client
async def to_start(query: CallbackQuery, client: Client):
    if client.subscription_is_active():
        await query.message.edit_text(
            start_short_msg_text,
            reply_markup=menu_kb,
        )
        return

    await query.message.edit_text(start_short_msg_text, reply_markup=start_kb)
