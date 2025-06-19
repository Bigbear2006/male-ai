from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from environs import env

env.read_env()


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

    YOOKASSA_RETURN_URL: str = field(default='https://t.me/vectorcore_bot')
    SUBSCRIPTION_PRICE: int = field(default=499)
    CURRENCY: str = field(default='RUB')
    SUPPORT_LINK: str = field(default='https://t.me/bottecda')
    PAGE_SIZE: int = field(default=5)
    TIME_FMT: str = field(default='%H:%M')
    DATE_FMT: str = field(default='%d.%m.%Y %H:%M')
    TZ: ZoneInfo = field(default=ZoneInfo('Europe/Moscow'))


config = Config()
