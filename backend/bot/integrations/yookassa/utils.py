from aiohttp import ClientResponse

from bot.config import config
from bot.integrations.yookassa.exceptions import YookassaException
from bot.loader import logger


def get_create_payment_payload(
    amount: float,
    description: str,
    email: str,
    payment_method_id: str | None = None,
) -> dict:
    payload = {
        'amount': {'value': amount, 'currency': config.CURRENCY},
        'capture': True,
        'confirmation': {
            'type': 'redirect',
            'return_url': config.BOT_LINK,
        },
        'description': description,
        'receipt': {
            'customer': {'email': email},
            'items': [
                {
                    'amount': {
                        'value': amount,
                        'currency': config.CURRENCY,
                    },
                    'description': description,
                    'vat_code': 1,
                    'quantity': 1,
                    'payment_subject': 'payment',
                    'payment_mode': 'full_payment',
                },
            ],
        },
        'save_payment_method': True,
    }
    if payment_method_id:
        payload['payment_method_id'] = payment_method_id
    else:
        payload['payment_method_data'] = {'type': 'bank_card'}
    return payload


async def get_data(rsp: ClientResponse) -> dict:
    data = await rsp.json()
    logger.info(data)
    if data.get('type') == 'error':
        raise YookassaException(data['description'])
    return data
