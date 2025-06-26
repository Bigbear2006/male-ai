import uuid

from aiohttp import BasicAuth

from bot.config import config
from bot.integrations.common.client import APIClient
from bot.integrations.yookassa.schemas import Payment, PaymentStatus
from bot.loader import logger


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

    async def create_payment(self, amount: float, description: str) -> Payment:
        async with self.session.post(
            '',
            headers=self.headers,
            json={
                'amount': {'value': amount, 'currency': config.CURRENCY},
                'payment_method_data': {'type': 'bank_card'},
                'capture': True,
                'confirmation': {
                    'type': 'redirect',
                    'return_url': config.YOOKASSA_RETURN_URL,
                },
                'description': description,
            },
        ) as rsp:
            data = await rsp.json()

        if not data.get('confirmation'):
            logger.info(data)

        return Payment(
            id=data['id'],
            confirmation_url=data['confirmation']['confirmation_url'],
        )

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        async with self.session.get(
            f'{payment_id}/',
            headers=self.headers,
        ) as rsp:
            data = await rsp.json()

        if not data.get('status'):
            logger.info(data)

        return PaymentStatus(data['status'])
