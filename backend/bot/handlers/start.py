from aiogram import F, Router, flags
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.start import menu_kb, start_kb
from bot.keyboards.utils import one_button_keyboard
from bot.loader import logger
from bot.states import ProfileState, StartState
from bot.utils.greetings import start_msg_text, start_short_msg_text
from bot.utils.validation import validate_email
from core.managers import get_or_none
from core.models import Client, Profile, PromoCode, Survey

router = Router()


@router.message(Command('start', 'menu'))
async def start(msg: Message, state: FSMContext, command: CommandObject):
    await state.set_state()

    client, created = await Client.objects.create_or_update(msg.from_user)
    if created:
        logger.info(f'New client {client} id={client.pk} was created')
        if promo_code := await get_or_none(PromoCode, pk=command.args):
            await Client.objects.update_by_id(
                client.pk,
                start_promo_code=promo_code,
            )
        await msg.answer(
            f'Ты получил пробный период на {promo_code.trial_days} дней '
            f'по промокоду {promo_code.code}!',
        )
    else:
        logger.info(f'Client {client} id={client.pk} was updated')

    if not client.email:
        await state.set_state(StartState.email)
        await msg.answer('Введи свою почту')
        return

    await client.arefresh_from_db()
    if await client.subscription_is_active():
        if await get_or_none(Profile, pk=client.pk):
            await msg.answer(start_short_msg_text, reply_markup=menu_kb)
            return

        if await get_or_none(Survey, pk=client.pk):
            await state.set_state(ProfileState.month_goal)
            await msg.answer(
                'Ты уже заполнил анкету. Давай теперь составим твой профиль.',
                reply_markup=one_button_keyboard(
                    text='Выбрать цель на 30 дней',
                    callback_data='entrust_ai',
                ),
            )
            return

        await msg.answer(
            start_msg_text,
            reply_markup=one_button_keyboard(
                text='Пройти анкетирование',
                callback_data='to_survey',
            ),
        )
        return

    await msg.answer(start_msg_text, reply_markup=start_kb)


@router.message(F.text, StateFilter(StartState.email))
async def set_client_email(msg: Message, state: FSMContext):
    email = await validate_email(msg)
    await Client.objects.filter(pk=msg.chat.id).aupdate(email=email)
    await state.set_state()
    await start(msg, state, CommandObject())


@router.callback_query(F.data == 'to_start')
@flags.with_client
async def to_start(query: CallbackQuery, client: Client):
    if await client.subscription_is_active():
        await query.message.edit_text(
            start_short_msg_text,
            reply_markup=menu_kb,
        )
        return

    await query.message.edit_text(start_short_msg_text, reply_markup=start_kb)
