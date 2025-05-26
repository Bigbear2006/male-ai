from asgiref.sync import sync_to_async

from core.choices import ManifestType
from core.models import Client, Habit, Profile, Survey
from core.utils import get_current_week_cycles_info

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
    survey = await Survey.objects.aget(pk=client.pk)
    profile = await Profile.objects.aget(pk=client.pk)
    cycles = await get_current_week_cycles_info(client.pk)
    habits = await sync_to_async(
        lambda: list(
            Habit.objects.filter(client=client).values_list('name', flat=True),
        ),
    )()

    return (
        f'Напиши настрой дня и микро-цель '
        f'по следующим данным пользователя:\n'
        f'{survey.info}\n\n'
        f'Профиль:\n{profile.info}\n\n'
        f'Привычки:\n{", ".join(habits)}\n\n'
        f'Дневник пользователя:\n{cycles}\n\n'
        f'Как хочет проявиться сегодня: {manifest_type.label}'
        f'{BASE_INSTRUCTIONS}'
    )


async def evening_support_prompt(client: Client):
    cycles = await get_current_week_cycles_info(client.pk)
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


def week_report_prompt():
    return (
        'Сформируй еженедельный мини-отчёт для пользователя:\n'
        '- сколько задач закрыл\n'
        '- в каких зонах есть рост\n'
        '- частые состояния'
        f'{BASE_INSTRUCTIONS}'
    )


def month_report_prompt():
    return (
        'Сформируй еженедельный мини-отчёт для пользователя:\n'
        '- сравни, где он был и где он сейчас\n'
        '- проанализируй стабильность, фокус, привычки\n'
        '- подскажи, что мешает, а что работает\n'
        '- можешь предложить обновить цели и стиль '
        '(мягкий/жёсткий/адаптивный)\n'
    )
