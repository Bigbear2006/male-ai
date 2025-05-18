from datetime import timedelta

from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from django.utils.timezone import now

from bot.config import config
from bot.keyboards.inline import back_to_start_kb
from bot.keyboards.utils import one_button_keyboard
from bot.states import SubscriptionState
from core.models import Client

router = Router()


@router.callback_query(F.data == 'buy_subscription')
async def buy_subscription(query: CallbackQuery):
    await query.message.edit_text(
        'Подписка стоит 1000 ₽ в месяц',
        reply_markup=one_button_keyboard(
            text='Оплатить',
            callback_data='pay_subscription',
            back_button_data='to_start',
        ),
    )


@router.callback_query(F.data == 'pay_subscription')
async def pay_subscription(query: CallbackQuery, state: FSMContext):
    await state.set_state(SubscriptionState.buying)
    await query.message.answer_invoice(
        'Оплата подписки',
        'Оплата подписки',
        'subscription',
        config.CURRENCY,
        [LabeledPrice(label='Подписка', amount=1000 * 100)],
        config.PROVIDER_TOKEN,
    )


@router.pre_checkout_query(SubscriptionState.buying)
async def accept_pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(True)


@router.message(F.successful_payment)
@flags.with_client
async def on_subscription_buying(
    msg: Message,
    state: FSMContext,
    client: Client,
):
    if client.subscription_end:
        subscription_end = client.subscription_end + timedelta(days=30)
    else:
        subscription_end = now() + timedelta(days=30)

    await Client.objects.update_by_id(
        msg.chat.id,
        subscription_end=subscription_end,
    )

    await state.clear()
    await msg.answer(
        'Поздравляем, теперь вам доступен полный доступ!\n\n'
        'Для начала надо пройти анкетирование.',
        reply_markup=one_button_keyboard(
            text='Пройти',
            callback_data='to_survey',
        ),
    )


@router.message(StateFilter(SubscriptionState.buying))
async def on_subscription_buying_error(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        'При оплате произошла какая-то ошибка',
        reply_markup=back_to_start_kb,
    )
