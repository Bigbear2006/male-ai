from bot.integrations.yookassa.client import YookassaClient
from bot.integrations.yookassa.schemas import Payment


async def create_payment(
    amount: float,
    description: str,
    email: str,
    payment_method_id: str | None = None,
) -> Payment:
    async with YookassaClient() as yookassa:
        return await yookassa.create_payment(
            amount,
            description,
            email,
            payment_method_id,
        )


async def get_payment(payment_id: str) -> Payment:
    async with YookassaClient() as yookassa:
        return await yookassa.get_payment(payment_id)
