from asgiref.sync import sync_to_async

from core.models import DailyCycle, Habit, Profile, Schedule, Survey


async def get_cycles_info(client_id: int, days: int = 7):
    cycles = DailyCycle.objects.get_recent_cycles(client_id, days)
    return '\n\n'.join([i.info async for i in cycles])


async def get_habits_info(client_id: int):
    habits = await sync_to_async(
        lambda: list(
            Habit.objects.filter(client_id=client_id).values_list(
                'name',
                flat=True,
            ),
        ),
    )()
    return ', '.join(habits)


async def get_schedule_info(client_id: int) -> str:
    schedule = await Schedule.objects.get_by_id(pk=client_id)
    return schedule.message_text


async def get_client_info(client_id: int):
    survey = await Survey.objects.aget(pk=client_id)
    profile = await Profile.objects.aget(pk=client_id)
    cycles = await get_cycles_info(client_id)
    habits = await get_habits_info(client_id)
    return (
        f'{survey.info}\n\n'
        f'Профиль:\n{profile.info}\n\n'
        f'Привычки:\n{", ".join(habits)}\n\n'
        f'Дневник пользователя:\n{cycles}\n\n'
    )
