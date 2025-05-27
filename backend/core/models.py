from datetime import time
from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now

from bot.config import config
from core.choices import (
    EnergyDirection,
    ManifestType,
    Priority,
    Purpose,
    ScheduleType,
    SpendTime,
    SupportOption,
    SupportStyle,
    UpgradeStyle,
)
from core.managers import (
    ClientManager,
    DailyCycleManager,
    ProfileManager,
    ScheduleManager,
    SurveyManager,
)


def strftime(__time: time):
    return __time.strftime(config.TIME_FMT)


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

    @property
    def info(self):
        return (
            f'Приоритет: {Priority(self.priority).label}\n'
            f'Готов уделять времени {SpendTime(self.spend_time).label}'
        )


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
        'Чего хочет достигнуть через 30 дней',
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
    objects = SurveyManager()

    class Meta:
        verbose_name = 'Анкета'
        verbose_name_plural = 'Анкеты'

    def __str__(self):
        return str(self.client)

    @property
    def info(self):
        energy_directions = ', '.join(
            [str(EnergyDirection(i).label) for i in self.energy_directions],
        )
        return (
            f'Как обращаться: {self.preferred_name}\n'
            f'Возраст: {self.age}\n'
            f'Внутреннее состояние: {self.shape}\n'
            f'Что последнее дало силы или радость: {self.last_forces_source}\n'
            f'Насколько доволен собой сейчас (1-10): {self.self_rating}\n'
            f'Куда чаще всего уходит энергия: {energy_directions}\n'
            f'Что сейчас важнее всего: {Purpose(self.purpose).label}\n'
            f'Чего хочет достигнуть через 30 дней: {self.future_version}\n'
            f'Стиль поддержки: {SupportStyle(self.support_style).label}\n'
            f'Что больше помогает, когда что-то идет не так: '
            f'{SupportOption(self.support_option).label}'
        )


class Profile(models.Model):
    client = models.OneToOneField(
        Client,
        models.CASCADE,
        primary_key=True,
        verbose_name='Пользователь',
    )
    start_point = models.TextField('Точка старта')
    month_goal = models.TextField('Цель на 30 дней')
    growth_zones = models.CharField(
        'В каких сферах жизни хотел бы прокачаться',
        max_length=255,
    )
    upgrade_style = models.CharField(
        'Стиль прокачки',
        max_length=20,
        choices=UpgradeStyle,
    )
    objects = ProfileManager()

    class Meta:
        verbose_name = 'Профиль 1.0'
        verbose_name_plural = 'Профили 1.0'

    def __str__(self):
        return str(self.client)

    @property
    def info(self):
        return (
            f'Цель на 30 дней: {self.month_goal}\n'
            f'В каких сферах жизни хотел бы прокачаться: {self.growth_zones}\n'
            f'Стиль прокачки: {UpgradeStyle(self.upgrade_style).label}'
        )


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


class DayResult(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'days_results',
        unique_for_date='created_at',
        verbose_name='Пользователь',
    )
    result = models.CharField(
        'Что получилось лучше, чем вчера',
        max_length=255,
    )
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Результат дня'
        verbose_name_plural = 'Ежедневные результаты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client} - {self.result[:50]}'


class DailyCycle(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'daily_cycles',
        unique_for_date='created_at',
        verbose_name='Пользователь',
    )
    manifest_type = models.CharField(
        'Как хочет проявиться',
        max_length=20,
        choices=ManifestType,
        blank=True,
    )
    morning_wellbeing = models.IntegerField(
        'Самочувствие утром',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )
    success_result = models.TextField('Что удалось', blank=True)
    fail_result = models.TextField('Что не получилось и почему', blank=True)
    feelings = models.TextField('Что почувствовал', blank=True)
    evening_wellbeing = models.IntegerField(
        'Самочувствие вечером',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    objects = DailyCycleManager()

    class Meta:
        verbose_name = 'Ежедневный цикл'
        verbose_name_plural = 'Ежедневные циклы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client} - {self.success_result[:50]}'

    @property
    def info(self):
        if self.manifest_type in ManifestType:
            manifest_type = ManifestType(self.manifest_type).label
        else:
            manifest_type = self.manifest_type

        return (
            f'Дата: {self.created_at.date()}'
            f'Как хочет проявиться: {manifest_type}'
            f'Самочувствие утром: {self.morning_wellbeing}'
            f'Что удалось: {self.success_result}'
            f'Что не получилось и почему: {self.fail_result}'
            f'Что почувствовал: {self.feelings}'
            f'Самочувствие вечером: {self.evening_wellbeing}'
        )


class Schedule(models.Model):
    client = models.OneToOneField(
        Client,
        models.CASCADE,
        primary_key=True,
        verbose_name='Пользователь',
    )
    schedule_type = models.CharField(
        'Тип расписания',
        max_length=255,
        choices=ScheduleType,
    )
    objects = ScheduleManager()

    class Meta:
        verbose_name = 'Режим дня'
        verbose_name_plural = 'Режимы дня'

    def __str__(self):
        return str(self.client)

    @property
    def message_text(self):
        blocks = '\n'.join([i.message_text for i in self.time_blocks.all()])
        return (
            f'Режим дня: {ScheduleType(self.schedule_type).label}\n\n'
            f'Блоки:\n{blocks}'
        )


class TimeBlock(models.Model):
    schedule = models.ForeignKey(Schedule, models.CASCADE, 'time_blocks')
    name = models.CharField('Название блока', max_length=255)
    start_time = models.TimeField('Дата начала')
    end_time = models.TimeField('Дата завершения', null=True)

    class Meta:
        verbose_name = 'Блок режима дня'
        verbose_name_plural = 'Блоки режимов дня'
        ordering = ['start_time']

    def __str__(self):
        return self.name

    @property
    def message_text(self):
        if self.end_time:
            return (
                f'{self.name}: '
                f'{strftime(self.start_time)} - {strftime(self.end_time)}'
            )
        return f'{self.name}: с {strftime(self.start_time)}'


class Course(models.Model):
    title = models.CharField('Название', max_length=255)
    url = models.URLField('Ссылка')

    class Meta:
        verbose_name = 'Микро курс'
        verbose_name_plural = 'Микро курсы'
        ordering = ['title']

    def __str__(self):
        return self.title


class Challenge(models.Model):
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    suitable_for = models.CharField('Подходит для', max_length=255)

    class Meta:
        verbose_name = 'Челлендж'
        verbose_name_plural = 'Челленджи'
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def message_text(self):
        return (
            f'Челлендж: {self.title}\n\n'
            f'Описание:\n{self.description}\n\n'
            f'Подходит для: {self.suitable_for}'
        )


class ChallengeTask(models.Model):
    challenge = models.ForeignKey(
        Challenge,
        models.CASCADE,
        'tasks',
        verbose_name='Челлендж',
    )
    day = models.IntegerField(
        'День',
        validators=[MinValueValidator(1)],
    )
    title = models.TextField('Задание')
    setup = models.TextField('Установка')

    class Meta:
        unique_together = ('challenge', 'day')
        verbose_name = 'Задание челленджа'
        verbose_name_plural = 'Задания челленджей'
        ordering = ['title']

    def __str__(self):
        return f'День {self.day}: {self.title[:50]}...'

    @property
    def message_text(self):
        return (
            f'Челлендж {self.challenge.title}\n\n'
            f'День {self.day}\n\n'
            f'Задание:\n{self.title}\n\n'
            f'Установка:\n{self.setup}'
        )


class ChallengeTaskQuestion(models.Model):
    task = models.ForeignKey(
        ChallengeTask,
        models.CASCADE,
        'questions',
        verbose_name='Задание челленджа',
    )
    title = models.CharField('Вопрос', max_length=255)

    class Meta:
        verbose_name = 'Вопрос к заданию челленджа'
        verbose_name_plural = 'Вопросы к заданиям челленджей'
        ordering = ['title']

    def __str__(self):
        return self.title


class ClientChallenge(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'challenges',
        verbose_name='Пользователь',
    )
    challenge = models.ForeignKey(
        Challenge,
        models.CASCADE,
        'clients',
        verbose_name='Челлендж',
    )
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        unique_together = ('client', 'challenge')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client} - {self.challenge}'


class ClientChallengeTaskQuestion(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'answers',
        verbose_name='Пользователь',
    )
    question = models.ForeignKey(
        ChallengeTaskQuestion,
        models.CASCADE,
        'clients',
        verbose_name='Вопрос',
    )
    answer = models.CharField('Ответ', max_length=255)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        unique_together = ('client', 'question')
        verbose_name = 'Ответ на вопрос челленджа'
        verbose_name_plural = 'Ответы на вопросы челленджей'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client} - {self.answer}'
