from bot.integrations.yookassa.client import YookassaClient
from bot.integrations.yookassa.schemas import Payment, PaymentStatus


async def create_payment(amount: float, description: str) -> Payment:
    async with YookassaClient() as yookassa:
        return await yookassa.create_payment(amount, description)


async def get_payment_status(payment_id: str) -> PaymentStatus:
    async with YookassaClient() as yookassa:
        return await yookassa.get_payment_status(payment_id)
