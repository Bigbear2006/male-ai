from dataclasses import dataclass, field

from environs import env

env.read_env()


@dataclass
class Config:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    PROVIDER_TOKEN: str = field(default_factory=lambda: env('PROVIDER_TOKEN'))
    OPENAI_API_KEY: str = field(default_factory=lambda: env('OPENAI_API_KEY'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))

    SUPPORT_LINK: str = field(default='https://t.me/bottecda')
    CURRENCY: str = field(default='RUB')
    PAGE_SIZE: int = field(default=5)
    TIME_FMT: str = field(default='%H:%M')


config = Config()
