from django.db import IntegrityError

from bot.loader import bot
from core.choices import AchievementType
from core.models import (
    Achievement,
    Client,
    ClientAchievement,
    ClientChallenge,
    ClientChallengeTaskQuestion,
    ClientSosButtonUsage,
    DailyCycle,
)


async def check_achievement(
    client_id: int | str,
    achievement_type: AchievementType,
    value: int,
):
    achievement = (
        await Achievement.objects.filter(
            achievement_type=achievement_type,
            value__lte=value,
        )
        .order_by('value')
        .afirst()
    )

    if not achievement:
        return

    if achievement_type == AchievementType.BOT_USAGE_WITHOUT_RESET:
        if DailyCycle.objects.get_max_gap(client_id) >= 3:
            return

    try:
        await ClientAchievement.objects.acreate(
            client_id=client_id,
            achievement=achievement,
        )
        await bot.send_message(client_id, achievement.message_text)
    except IntegrityError:
        pass

    if achievement_type != AchievementType.ACHIEVEMENTS_COLLECTION:
        await check_achievements_collection(client_id)


async def check_sos_button_usages(client_id: int | str):
    usages = await ClientSosButtonUsage.objects.get_usages(client_id)
    return await check_achievement(
        client_id,
        AchievementType.SOS_BUTTON_USAGE,
        usages,
    )


async def check_completed_challenges(client_id: int | str):
    completed = await ClientChallenge.objects.get_completed_count(client_id)
    return await check_achievement(
        client_id,
        AchievementType.CHALLENGE_COMPLETED,
        completed,
    )


async def check_challenge_tasks_streak(client_id: int | str):
    streak = await ClientChallengeTaskQuestion.objects.get_streak(client_id)
    return await check_achievement(
        client_id,
        AchievementType.CHALLENGE_TASKS_STREAK,
        streak,
    )


async def check_started_challenges(client_id: int | str):
    started_count = await ClientChallenge.objects.get_started_count(client_id)
    return await check_achievement(
        client_id,
        AchievementType.START_CHALLENGE,
        started_count,
    )


async def check_daily_cycles_streak(client_id: int | str):
    cycles = await DailyCycle.objects.get_count(client_id)
    return await check_achievement(
        client_id,
        AchievementType.DAILY_CYCLES_STREAK,
        cycles,
    )


async def check_bot_usage(client: Client):
    return await check_achievement(
        client.pk,
        AchievementType.BOT_USAGE,
        client.get_bot_usage_days(),
    )


async def check_bot_usage_without_reset(client: Client):
    return await check_achievement(
        client.pk,
        AchievementType.BOT_USAGE_WITHOUT_RESET,
        client.get_bot_usage_days(),
    )


async def check_achievements_collection(client_id: int | str):
    achievements = await ClientAchievement.objects.get_count(client_id)
    return await check_achievement(
        client_id,
        AchievementType.ACHIEVEMENTS_COLLECTION,
        achievements,
    )
