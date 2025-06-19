from bot.common.ai.context import (
    get_client_info,
    get_cycles_info,
    get_habits_info,
    get_schedule_info,
)
from bot.common.time_utils import current_time
from core.choices import ManifestType, PromptType
from core.models import Client, Profile, Prompt, Survey


async def state_analysis_prompt(survey: Survey):
    prompt = await Prompt.objects.aget(prompt_type=PromptType.STATE_ANALYSIS)
    return f'{prompt.text}\n{survey.info}'


async def select_month_goal_prompt(survey: Survey):
    prompt = await Prompt.objects.aget(
        prompt_type=PromptType.SELECT_MONTH_GOAL,
    )
    return f'{prompt.text}\n{survey.info}'


async def morning_message_prompt(client: Client):
    prompt = await Prompt.objects.aget(prompt_type=PromptType.MORNING_MESSAGE)
    return f'{prompt.text}\n{client.info}'


async def morning_extended_message_prompt(
    client: Client,
    manifest_type: ManifestType,
):
    prompt = await Prompt.objects.aget(
        prompt_type=PromptType.MORNING_EXTENDED_MESSAGE,
    )
    info = await get_client_info(client.pk)
    return (
        f'{prompt.text}\n{info}\n'
        f'Какой настрой выбрал сегодня: {manifest_type.label}'
    )


async def day_message_prompt(client_id: int | str):
    prompt = await Prompt.objects.aget(prompt_type=PromptType.DAY_MESSAGE)
    schedule = await get_schedule_info(client_id)
    habits = await get_habits_info(client_id)
    return (
        f'{prompt.text}\n'
        f'Текущее время: {current_time()}\n'
        f'Режим пользователя:\n{schedule}\n'
        f'Привычки:\n{habits}'
    )


async def evening_support_prompt(client: Client):
    prompt = await Prompt.objects.aget(prompt_type=PromptType.EVENING_SUPPORT)
    cycles = await get_cycles_info(client.pk)
    return f'{prompt.text}\n{cycles}'


async def select_overload_method(user_msg: str):
    prompt = await Prompt.objects.aget(
        prompt_type=PromptType.SELECT_OVERLOAD_METHOD,
    )
    return f'{prompt.text}\n{user_msg}\n'


async def get_sos_help():
    prompt = await Prompt.objects.aget(prompt_type=PromptType.GET_SOS_HELP)
    return prompt.text


async def week_report_prompt(client_id: int | str):
    prompt = await Prompt.objects.aget(prompt_type=PromptType.WEEK_REPORT)
    cycles_info = await get_cycles_info(client_id)
    return f'{prompt.text}\n{cycles_info}\n'


async def month_report_prompt(client_id: int | str):
    prompt = await Prompt.objects.aget(prompt_type=PromptType.MONTH_REPORT)
    cycles_info = await get_cycles_info(client_id, days=30)
    profile = await Profile.objects.aget(pk=client_id)
    return f'{prompt.text}\n\n{cycles_info}\n\nПрофиль:\n{profile.info}'
