from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True)
class Payment:
    id: str
    confirmation_url: str


class PaymentStatus(StrEnum):
    """https://yookassa.ru/developers/payment-acceptance/getting-started/payment-process#lifecycle"""

    PENDING = 'pending'
    WAITING_FOR_CAPTURE = 'waiting_for_capture'
    SUCCEEDED = 'succeeded'
    CANCELED = 'canceled'
