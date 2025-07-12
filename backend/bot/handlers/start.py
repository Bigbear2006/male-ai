from aiogram import F, Router, flags
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InputMediaDocument,
    Message,
)

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
        await msg.answer_media_group(
            [
                InputMediaDocument(
                    media=BufferedInputFile.from_file(
                        'assets/documents/1. Политика обработки ПС.docx',
                    ),
                ),
                InputMediaDocument(
                    media=BufferedInputFile.from_file(
                        'assets/documents/2. Согласие на обработку ПС.docx',
                    ),
                ),
                InputMediaDocument(
                    media=BufferedInputFile.from_file(
                        'assets/documents/3_Форма_запроса_на_предоставление_обрбатываемых_ПС.docx',
                    ),
                ),
                InputMediaDocument(
                    media=BufferedInputFile.from_file(
                        'assets/documents/4_Форма_отзыва_согласия_на_обработку_ПС.docx',
                    ),
                ),
                InputMediaDocument(
                    media=BufferedInputFile.from_file(
                        'assets/documents/Публичная_оферта_и_правила_использования.docx',
                    ),
                ),
            ],
        )
        await msg.answer(
            '<b>ООО «ИП Лазарева» — '
            'Информация о сборе персональных данных</b>\n\n'
            'Мы собираем и обрабатываем ваши '
            'персональные данные в соответствии'
            'с Федеральным законом №152-ФЗ '
            '«О персональных данных».\n\n'
            'Перед началом заполнения формы ознакомьтесь '
            'с нашими документами.\n\n'
            'Ваши данные используются строго для указанных целей '
            'и защищены от несанкционированного доступа.\n'
            'У вас всегда есть право запросить удаление '
            'или изменение своих данных.',
            parse_mode=ParseMode.HTML,
            reply_markup=one_button_keyboard(
                text='✅ Ознакомлен и согласен',
                callback_data='approve_data_processing',
            ),
        )
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


@router.callback_query(F.data == 'approve_data_processing')
async def approve_data_processing(query: CallbackQuery, state: FSMContext):
    await state.set_state(StartState.email)
    await query.message.answer(
        'Введи свою почту. Она нужна для отправки чеков',
    )


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
