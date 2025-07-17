from datetime import timedelta
from typing import TYPE_CHECKING, Optional

from aiogram import types
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.timezone import now

from core.choices import ScheduleType

if TYPE_CHECKING:
    from core.models import Client, Profile, Schedule, Survey


class ClientManager(models.Manager):
    async def from_tg_user(self, user: types.User) -> 'Client':
        return await self.acreate(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium or False,
        )

    async def update_from_tg_user(self, user: types.User) -> None:
        await self.filter(pk=user.id).aupdate(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium or False,
        )

    async def create_or_update(
        self,
        user: types.User,
    ) -> tuple['Client', bool]:
        try:
            client = await self.aget(pk=user.id)
            await self.update_from_tg_user(user)
            await client.arefresh_from_db()
            return client, False
        except ObjectDoesNotExist:
            return await self.from_tg_user(user), True

    async def update_by_id(self, pk: int | str, **kwargs):
        await self.filter(pk=pk).aupdate(**kwargs)

    def get_subscribed(self, *, exclude_survey_unfilled: bool = False):
        today = now()
        qs = self.filter(
            models.Q(subscription_end__gte=today)
            | models.Q(created_at__gte=today - timedelta(days=7)),
        )
        if exclude_survey_unfilled:
            return qs.exclude(
                survey__isnull=True,
                profile__isnull=True,
            )
        return qs

    def get_unsubscribed(self, *, exclude_survey_unfilled: bool = False):
        qs = self.filter(
            models.Q(subscription_end__isnull=True)
            | models.Q(subscription_end__lt=now()),
        )
        if exclude_survey_unfilled:
            return qs.exclude(priority='', spend_time='')
        return qs


class SurveyManager(models.Manager):
    async def create_or_update(
        self,
        client_id: int | str,
        **defaults,
    ) -> 'Survey':
        survey, _ = await self.aupdate_or_create(
            defaults,
            {**defaults, 'client_id': client_id},
            client_id=client_id,
        )
        return survey


class ProfileManager(models.Manager):
    async def create_or_update(
        self,
        client_id: int | str,
        **defaults,
    ) -> 'Profile':
        profile, _ = await self.aupdate_or_create(
            defaults,
            {**defaults, 'client_id': client_id},
            client_id=client_id,
        )
        return profile


class DailyCycleManager(models.Manager):
    def get_recent_cycles(self, client_id: int, days: int = 7):
        return self.filter(client_id=client_id)[:days]

    async def create_or_update(
        self,
        client_id: int | str,
        **defaults,
    ) -> 'Profile':
        cycle, _ = await self.aupdate_or_create(
            defaults,
            {**defaults, 'client_id': client_id},
            client_id=client_id,
            created_at__date=now().date(),
        )
        return cycle

    async def get_count(self, client_id: int | str):
        return await self.filter(client_id=client_id).acount()

    async def get_max_gap(self, client_id: int | str, days: int = 60):
        cycles = await sync_to_async(
            lambda: list(
                self.filter(
                    client_id=client_id,
                    created_at__date__gte=now().date() - timedelta(days=days),
                ).order_by('created_at'),
            ),
        )()

        max_gap = 0
        for i, cycle in enumerate(cycles):
            if i == 0:
                continue
            gap = (
                cycle.created_at.date() - cycles[i - 1].created_at.date()
            ).days - 1
            if gap > max_gap:
                max_gap = gap
        return max_gap


class ScheduleManager(models.Manager):
    async def get_by_id(self, pk: int | str) -> Optional['Schedule']:
        try:
            return await self.prefetch_related('time_blocks').aget(pk=pk)
        except ObjectDoesNotExist:
            return

    async def create_or_update(
        self,
        client_id: int | str,
        schedule_type: ScheduleType,
    ) -> 'Schedule':
        schedule, _ = await self.aupdate_or_create(
            {'schedule_type': schedule_type},
            {'schedule_type': schedule_type, 'client_id': client_id},
            client_id=client_id,
        )
        return schedule


class ChallengeTaskManager(models.Manager):
    async def get_last_day(self, challenge_id: int | str) -> int:
        return (
            await self.filter(challenge_id=challenge_id).aaggregate(
                last_day=models.Max(
                    'day',
                    filter=models.Q(questions__isnull=False),
                    default=0,
                ),
            )
        )['last_day']


class ClientChallengeManager(models.Manager):
    def get_completed(self, client_id: int | str):
        return self.filter(client_id=client_id, completed_at__isnull=False)

    def get_subscribed(self):
        return self.filter(client__subscription_end__gte=now())

    async def get_completed_count(self, client_id: int | str) -> int:
        return await self.get_completed(client_id).acount()

    async def get_started_count(self, client_id: int | str):
        return await self.filter(client_id=client_id).acount()


class ClientChallengeTaskQuestionManager(models.Manager):
    async def create_or_update(self, client_id: int | str, **defaults):
        task, _ = await self.aupdate_or_create(
            defaults,
            {**defaults, 'client_id': client_id},
            client_id=client_id,
        )
        return task

    async def get_last_completed_day(
        self,
        client_id: int | str,
        challenge_id: int | str,
    ) -> int:
        return (
            await self.filter(
                client_id=client_id,
                question__task__challenge_id=challenge_id,
            ).aaggregate(last_day=models.Max('question__task__day', default=0))
        )['last_day']

    async def get_streak(self, client_id: int | str) -> int:
        days = await sync_to_async(
            lambda: list(
                self.filter(client_id=client_id)
                .values_list('created_at__date', flat=True)
                .order_by('created_at__date')
                .distinct('created_at__date'),
            ),
        )()

        streak = 0
        for i, day in enumerate(days):
            if i == 0:
                streak += 1
                continue
            if (day - days[i - 1]).days > 1:
                break
            streak += 1
        return streak

    async def get_recent(self, client_id: int | str, days: int = 7):
        return self.select_related('question__task').filter(
            client_id=client_id,
            created_at__date__gte=now().date() - timedelta(days=days),
        )


class ClientSosButtonUsageManager(models.Manager):
    async def get_usages(self, client_id: int | str):
        return await self.filter(client_id=client_id).acount()


class ClientAchievementManager(models.Manager):
    async def get_count(self, client_id: int | str):
        return await self.filter(client_id=client_id).acount()


async def get_or_none(model: type[models.Model], *args, **kwargs):
    try:
        return await model.objects.aget(*args, **kwargs)
    except ObjectDoesNotExist:
        return
