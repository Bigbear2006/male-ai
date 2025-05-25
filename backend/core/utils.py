from datetime import timedelta

from django.utils.timezone import now

from core.models import DailyCycle


async def get_current_week_cycles(client_id: int):
    today = now().date()
    first_week_day = today - timedelta(days=today.weekday())
    last_week_day = first_week_day + timedelta(days=6)
    return DailyCycle.objects.filter(
        client_id=client_id,
        created_at__date__gte=first_week_day,
        created_at__date__lte=last_week_day,
    )


async def get_current_week_cycles_info(client_id: int):
    return '\n\n'.join(
        [i.info async for i in await get_current_week_cycles(client_id)],
    )
