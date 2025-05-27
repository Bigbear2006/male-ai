from datetime import timedelta
from typing import TYPE_CHECKING, Optional

from aiogram import types
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
        qs = self.filter(subscription_end__gte=now())
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
        return self.filter(
            client_id=client_id,
            created_at__date__gte=now().date() - timedelta(days=days),
        )

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
