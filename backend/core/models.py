from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now

from core.choices import (
    EnergyDirection,
    Priority,
    Purpose,
    SpendTime,
    SupportOption,
    SupportStyle,
    UpgradeStyle,
)
from core.managers import ClientManager


class User(AbstractUser):
    pass


class Client(models.Model):
    id = models.PositiveBigIntegerField('Telegram ID', primary_key=True)
    first_name = models.CharField('Имя', max_length=255)
    last_name = models.CharField(
        'Фамилия',
        max_length=255,
        null=True,
        blank=True,
    )
    username = models.CharField('Ник', max_length=32, null=True, blank=True)
    is_premium = models.BooleanField('Есть премиум', default=False)
    subscription_end = models.DateTimeField(
        'Дата окончания подписки',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    priority = models.CharField(
        'Приоритет',
        max_length=50,
        choices=Priority,
        blank=True,
    )
    spend_time = models.CharField(
        'Готов уделять времени',
        max_length=10,
        choices=SpendTime,
        blank=True,
    )
    objects = ClientManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        username = self.first_name
        if self.username:
            username += f' (@{self.username})'
        return username

    def subscription_is_active(self) -> bool:
        if not self.subscription_end:
            return False
        return self.subscription_end >= now()

    def free_survey_filled(self) -> bool:
        return bool(self.priority) and bool(self.spend_time)

    async def has_profile(self) -> Optional['Profile']:
        try:
            return await Profile.objects.aget(pk=self.pk)
        except ObjectDoesNotExist:
            return


class Survey(models.Model):
    client = models.OneToOneField(
        Client,
        models.CASCADE,
        primary_key=True,
        verbose_name='Пользователь',
    )
    preferred_name = models.CharField('Как обращаться', max_length=255)
    age = models.CharField('Возраст', max_length=10)
    shape = models.CharField('Внутреннее состояние', max_length=255)
    last_forces_source = models.CharField(
        'Что последнее дало силы или радость',
        max_length=255,
    )
    self_rating = models.IntegerField(
        'Самооценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    energy_directions = ArrayField(
        models.CharField(max_length=50, choices=EnergyDirection),
        verbose_name='Куда чаще всего уходит энергия',
    )
    purpose = models.CharField(
        'Что сейчас важнее всего',
        max_length=50,
        choices=Purpose,
    )
    future_version = models.CharField(
        'Кем хочет стать через 30 дней',
        max_length=255,
    )
    support_style = models.CharField(
        'Стиль поддержки',
        max_length=50,
        choices=SupportStyle,
    )
    support_option = models.CharField(
        'Что больше помогает, когда что-то идёт не так',
        max_length=50,
        choices=SupportOption,
    )
    key_quality = models.CharField(
        'Качество, которое хочется усилить',
        max_length=255,
    )

    class Meta:
        verbose_name = 'Анкета'
        verbose_name_plural = 'Анкеты'

    def __str__(self):
        return str(self.client)


class Profile(models.Model):
    client = models.OneToOneField(
        Client,
        models.CASCADE,
        primary_key=True,
        verbose_name='Пользователь',
    )
    start_point = models.TextField('Точка старта')
    month_goal = models.TextField('Цель на 30 дней')
    growth_zones = models.CharField('Зоны роста', max_length=255)
    upgrade_style = models.CharField(
        'Стиль прокачки',
        max_length=20,
        choices=UpgradeStyle,
    )

    class Meta:
        verbose_name = 'Профиль 1.0'
        verbose_name_plural = 'Профили 1.0'

    def __str__(self):
        return str(self.client)


class Habit(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'habits',
        verbose_name='Пользователь',
    )
    name = models.CharField('Название', max_length=255)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
