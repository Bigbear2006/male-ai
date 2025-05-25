from datetime import timedelta
from typing import TYPE_CHECKING

from aiogram import types
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.timezone import now

if TYPE_CHECKING:
    from core.models import Client


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

    async def update_by_id(self, pk: int, **kwargs):
        await self.filter(pk=pk).aupdate(**kwargs)

    def get_subscribed(self):
        return self.filter(subscription_end__gte=now())

    def get_unsubscribed(self, *, exclude_survey_unfilled: bool = False):
        qs = self.filter(
            models.Q(subscription_end__isnull=True)
            | models.Q(subscription_end__lt=now()),
        )
        if exclude_survey_unfilled:
            return qs.exclude(priority='', spend_time='')
        return qs


class DailyCycleManager(models.Manager):
    def get_current_week(self, client_id: int):
        today = now().date()
        first_week_day = today - timedelta(days=today.weekday())
        last_week_day = first_week_day + timedelta(days=6)
        return self.filter(
            client_id=client_id,
            created_at__date__gte=first_week_day,
            created_at__date__lte=last_week_day,
        )
