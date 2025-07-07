from dataclasses import dataclass
from enum import StrEnum


class PaymentStatus(StrEnum):
    """https://yookassa.ru/developers/payment-acceptance/getting-started/payment-process#lifecycle"""

    PENDING = 'pending'
    WAITING_FOR_CAPTURE = 'waiting_for_capture'
    SUCCEEDED = 'succeeded'
    CANCELED = 'canceled'


@dataclass(frozen=True)
class Payment:
    id: str
    confirmation_url: str
    payment_method_id: str
    status: PaymentStatus

    @classmethod
    def from_dict(cls, data: dict) -> 'Payment':
        return cls(
            id=data['id'],
            confirmation_url=data.get('confirmation', {}).get(
                'confirmation_url',
            ),
            payment_method_id=data['payment_method']['id'],
            status=PaymentStatus(data['status']),
        )
