import uuid

from aiohttp import BasicAuth

from bot.config import config
from bot.integrations.common.client import APIClient
from bot.integrations.yookassa.schemas import Payment
from bot.integrations.yookassa.utils import (
    get_create_payment_payload,
    get_data,
)


class YookassaClient(APIClient):
    def __init__(self, **session_kwargs):
        super().__init__(
            'https://api.yookassa.ru/v3/payments/',
            auth=self.auth,
            **session_kwargs,
        )

    @property
    def auth(self):
        return BasicAuth(config.YOOKASSA_SHOP_ID, config.YOOKASSA_SECRET_KEY)

    @property
    def headers(self):
        return {'Idempotence-Key': str(uuid.uuid4())}

    async def create_payment(
        self,
        amount: float,
        description: str,
        email: str,
        payment_method_id: str | None = None,
    ) -> Payment:
        async with self.session.post(
            '',
            headers=self.headers,
            json=get_create_payment_payload(
                amount,
                description,
                email,
                payment_method_id,
            ),
        ) as rsp:
            data = await get_data(rsp)
        return Payment.from_dict(data)

    async def get_payment(self, payment_id: str) -> Payment:
        async with self.session.get(
            f'{payment_id}/',
            headers=self.headers,
        ) as rsp:
            data = await get_data(rsp)
        return Payment.from_dict(data)
