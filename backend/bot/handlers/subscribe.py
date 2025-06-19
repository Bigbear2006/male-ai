from datetime import timedelta

from aiogram import F, Router, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from django.utils.timezone import now

from bot.config import config
from bot.integrations.yookassa import (
    PaymentStatus,
    create_payment,
    get_payment_status,
)
from bot.keyboards.start import back_to_start_kb
from bot.keyboards.subscribe import pay_subscription_kb
from bot.keyboards.utils import one_button_keyboard
from bot.states import SubscriptionState
from core.models import Client

router = Router()


@router.callback_query(F.data == 'buy_subscription')
async def buy_subscription(query: CallbackQuery):
    await query.message.edit_text(
        f'Подписка стоит {config.SUBSCRIPTION_PRICE} ₽ в месяц',
        reply_markup=one_button_keyboard(
            text='Оплатить',
            callback_data='pay_subscription',
            back_button_data='to_start',
        ),
    )


@router.callback_query(F.data == 'pay_subscription')
async def pay_subscription(query: CallbackQuery, state: FSMContext):
    await state.set_state(SubscriptionState.buying)
    payment = await create_payment(
        config.SUBSCRIPTION_PRICE,
        'Оплата подписки',
    )
    await state.update_data(payment_id=payment.id)
    await query.message.edit_text(
        f'Ваша ссылка на оплату:\n\n{payment.confirmation_url}',
        reply_markup=pay_subscription_kb,
    )


@router.callback_query(F.data == 'check_subscription_buying')
@flags.with_client
async def on_subscription_buying(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    status = await get_payment_status(await state.get_value('payment_id'))
    if not status == PaymentStatus.SUCCEEDED:
        await query.answer(
            'К сожалению оплата не прошла. Попробуйте еще раз.',
            show_alert=True,
        )
        return

    if client.subscription_end:
        subscription_end = client.subscription_end + timedelta(days=30)
    else:
        subscription_end = now() + timedelta(days=30)

    await Client.objects.update_by_id(
        client.id,
        subscription_end=subscription_end,
    )
    await state.clear()

    if await client.has_profile():
        await query.message.edit_text(
            'Вы продлили подписку на месяц',
            reply_markup=back_to_start_kb,
        )
        return

    await query.message.edit_text(
        'Поздравляем, теперь вам доступен полный доступ!\n\n'
        'Для начала надо пройти анкетирование.',
        reply_markup=one_button_keyboard(
            text='Пройти',
            callback_data='to_survey',
        ),
    )


@router.callback_query(F.data == 'cancel_subscription_buying')
async def cancel_subscription_buying(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text(
        'Платеж отменен',
        reply_markup=back_to_start_kb,
    )
