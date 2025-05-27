from bot.client_info import (
    get_client_info,
    get_cycles_info,
    get_habits_info,
    get_schedule_info,
)
from bot.time_utils import current_time
from core.choices import ManifestType
from core.models import Client, Survey

BASE_INSTRUCTIONS = (
    'ВАЖНО:\nОбращайся прямо к этому человеку.\nНе нужно ставить ** и ###\n'
)


def state_analysis_prompt(survey: Survey):
    return (
        f'Проанализируй состояние человека по следующим данным:\n'
        f'{survey.info}\n\n{BASE_INSTRUCTIONS}'
    )


def select_month_goal_prompt(survey: Survey):
    return (
        f'Предложи цель на месяц по следующим данным:\n'
        f'{survey.info}'
        f'ВАЖНО:\n'
        f'Сформулируй цель, не надо расписывать шаги.\n'
        f'Не нужно писать само слово цель и двоеточие в начале.\n'
        f'Не нужно ставить ** и ###'
    )


def morning_message_prompt(client: Client):
    return (
        f'Напиши настрой дня и микро-цель:\n'
        f'Данные пользователя:\n{client.info}'
        f'{BASE_INSTRUCTIONS}'
    )


async def morning_extended_message_prompt(
    client: Client,
    manifest_type: ManifestType,
):
    info = await get_client_info(client.pk)
    return (
        f'Напиши настрой дня и микро-цель '
        f'по следующим данным пользователя:\n{info}'
        f'Как хочет проявиться сегодня: {manifest_type.label}'
        f'{BASE_INSTRUCTIONS}'
    )


async def day_message_prompt(client_id: int | str):
    schedule = await get_schedule_info(client_id)
    habits = await get_habits_info(client_id)
    return (
        f'Напиши пользователю что-нибудь мотивирующее,'
        f'учитывай текущее время и режим дня пользователя. '
        f'Можешь напомнить ему про привычки\n\n'
        f'Текущее время: {current_time()}\n'
        f'Режим пользователя:\n{schedule}\n'
        f'Привычки:\n{habits}'
    )


async def evening_support_prompt(client: Client):
    cycles = await get_cycles_info(client.pk)
    return (
        f'Вот дневник пользователя за эту неделю:\n{cycles}'
        f'Поддержи его\n\n{BASE_INSTRUCTIONS}'
    )


def select_overload_method(user_msg: str):
    return (
        'Пользователь пишет:\n'
        f'{user_msg}\n'
        'С учетом настроя пользователя выбери технику перегрузки, '
        'и обращаясь прямо к пользователю, скажи, что ему следует сделать:\n'
        '- центрирование через дыхание\n'
        '- фокус через вопрос'
        '- быстрое микро-действие'
        '- перенаправление внимания'
        '- эмоциональная выгрузка'
        f'{BASE_INSTRUCTIONS}'
    )


def get_sos_help():
    return (
        'Пользователь описывает ситуацию, а ты даёшь совет — '
        'далее просишь написать, например, "Опиши что ты сейчас чувствуешь" — '
        'и далее так-же ведёшь диалог.\n'
        'Тебе нужно нужно закончить диалог за 3 сообщения.'
        'В 1 и 2 сообщении задавай вопросы для уточнения, '
        'а в третьем подводи итог и завершай.\n'
        f'{BASE_INSTRUCTIONS}'
    )


async def week_report_prompt(client_id: int | str):
    cycles_info = await get_cycles_info(client_id)
    return (
        'Сформируй еженедельный мини-отчёт для пользователя:\n'
        '- сколько задач закрыл\n'
        '- в каких зонах есть рост\n'
        '- частые состояния\n'
        f'Дневник пользователя:\n{cycles_info}\n'
        f'{BASE_INSTRUCTIONS}'
    )


async def month_report_prompt(client_id: int | str):
    cycles_info = await get_cycles_info(client_id, days=30)
    return (
        'Сформируй месячный отчёт для пользователя:\n'
        '- сравни, где он был и где он сейчас\n'
        '- проанализируй стабильность, фокус, привычки\n'
        '- подскажи, что мешает, а что работает\n'
        '- можешь предложить обновить цели и стиль '
        '(мягкий/жёсткий/адаптивный)\n'
        f'Дневник пользователя:\n{cycles_info}\n'
        f'{BASE_INSTRUCTIONS}'
    )
