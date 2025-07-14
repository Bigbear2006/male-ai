from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from environs import env

env.read_env()


@dataclass
class Media:
    privacy_policy_doc: str = ''
    consent_to_process_doc: str = ''
    data_request_form_doc: str = ''
    consent_withdrawal_form_doc: str = ''
    public_offer_doc: str = ''


@dataclass
class Config:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    OPENAI_API_KEY: str = field(default_factory=lambda: env('OPENAI_API_KEY'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))
    YOOKASSA_SHOP_ID: str = field(
        default_factory=lambda: env('YOOKASSA_SHOP_ID'),
    )
    YOOKASSA_SECRET_KEY: str = field(
        default_factory=lambda: env('YOOKASSA_SECRET_KEY'),
    )

    BOT_LINK: str = field(default='https://t.me/vectorcore_bot')
    CURRENCY: str = field(default='RUB')
    SUPPORT_LINK: str = field(default='https://t.me/bottecda')
    PAGE_SIZE: int = field(default=5)
    TIME_FMT: str = field(default='%H:%M')
    DATE_FMT: str = field(default='%d.%m.%Y %H:%M')
    TZ: ZoneInfo = field(default=ZoneInfo('Europe/Moscow'))

    POLICY_URL: str = field(
        default='https://docs.google.com/document/d/1ArfYBta4Mtl5-lL8_7rZtge6w21Rg1Zv/edit?usp=share_link&ouid=104573866277679126439&rtpof=true&sd=true',
    )
    CONSENT_URL: str = field(
        default='https://docs.google.com/document/d/1f9LZQvhV9kyocH60ugh4RFK0sOgQzO4_/edit?usp=share_link&ouid=104573866277679126439&rtpof=true&sd=true',
    )
    REQUEST_FORM_URL: str = field(
        default='https://docs.google.com/document/d/1cfwnB1eMFQpM5KJLwlo5YXvtqCTxLEjW/edit?usp=share_link&ouid=104573866277679126439&rtpof=true&sd=true',
    )
    REVOCATION_FORM_URL: str = field(
        default='https://docs.google.com/document/d/17seSruXBxuIswK40a8O_RPjSwqRClsW_/edit?usp=share_link&ouid=104573866277679126439&rtpof=true&sd=true',
    )
    OFFER_URL: str = field(
        default='docs.google.com/document/d/17seSruXBxuIswK40a8O_RPjSwqRClsW_/edit?usp=share_link&ouid=104573866277679126439&rtpof=true&sd=true',
    )


config = Config()
