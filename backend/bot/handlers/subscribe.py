from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.integrations.yookassa import (
    PaymentStatus,
    create_payment,
)
from bot.integrations.yookassa.service import get_payment
from bot.keyboards.start import back_to_start_kb
from bot.keyboards.subscribe import (
    pay_subscription_kb,
    subscribe_kb,
    to_subscribe_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.services.promo_code import promo_code_is_active
from bot.states import SubscriptionState
from core.managers import get_or_none
from core.models import (
    Client,
    PromoCode,
    PromoCodeActivation,
    SubscriptionPrice,
)

router = Router()


@router.callback_query(F.data == 'buy_subscription')
@flags.with_client(select_related=('start_promo_code',))
async def buy_subscription(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    price = await SubscriptionPrice.objects.afirst()
    promo = client.start_promo_code
    if promo_code_id := await state.get_value('promo_code_id'):
        promo = await PromoCode.objects.aget(pk=promo_code_id)

    text = f'Подписка стоит {price.price} ₽ в месяц\n\n'
    if await promo_code_is_active(promo):
        await state.update_data(promo_code_id=promo.pk)
        text += (
            f'Вы активировали скидку {promo.discount}%'
            f' по промокоду {promo.code}'
        )

    await state.set_state()
    await query.message.edit_text(text, reply_markup=subscribe_kb)


@router.callback_query(F.data == 'activate_promo_code')
async def activate_promo_code(query: CallbackQuery, state: FSMContext):
    await state.set_state(SubscriptionState.promo_code)
    await query.message.edit_text(
        'Введите промокод',
        reply_markup=to_subscribe_kb,
    )


@router.message(F.text, StateFilter(SubscriptionState.promo_code))
async def set_promo_code(msg: Message, state: FSMContext):
    promo_code = await get_or_none(PromoCode, pk=msg.text)
    if promo_code:
        await state.update_data(promo_code_id=promo_code.pk)
        await msg.answer(
            f'Промокод {promo_code.code} добавлен!',
            reply_markup=to_subscribe_kb,
        )
        return
    await msg.answer('Такого промокода нет', reply_markup=to_subscribe_kb)


@router.callback_query(F.data == 'pay_subscription')
@flags.with_client
async def pay_subscription(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    price = (await SubscriptionPrice.objects.afirst()).price
    promo_code = await get_or_none(
        PromoCode,
        pk=await state.get_value('promo_code_id'),
    )
    if await promo_code_is_active(promo_code):
        price = price * ((100 - promo_code.discount) / 100)
    payment = await create_payment(price, 'Оплата подписки', client.email)

    await state.update_data(payment_id=payment.id)
    await state.set_state(SubscriptionState.buying)
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
    data = await state.get_data()
    payment = await get_payment(data['payment_id'])
    if payment.status != PaymentStatus.SUCCEEDED:
        await query.answer(
            'К сожалению оплата не прошла. Попробуйте еще раз.',
            show_alert=True,
        )
        return

    if promo_code_id := data.get('promo_code_id', None):
        await PromoCodeActivation.objects.acreate(
            client=client,
            promo_code_id=promo_code_id,
        )

    subscription_end = await client.prolong_subscription(auto_save=False)
    await Client.objects.update_by_id(
        client.id,
        subscription_end=subscription_end,
        payment_method_id=payment.payment_method_id,
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
