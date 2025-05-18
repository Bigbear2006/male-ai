from dataclasses import dataclass, field

from environs import env

env.read_env()


@dataclass
class Config:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    PROVIDER_TOKEN: str = field(default_factory=lambda: env('PROVIDER_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))

    SUPPORT_LINK: str = field(default='https://t.me/bottecda')
    CURRENCY: str = field(default='RUB')


config = Config()
