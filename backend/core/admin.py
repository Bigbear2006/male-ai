from django.contrib import admin
from django.contrib.auth.models import Group

from core import models

admin.site.unregister(Group)

admin.site.register(models.Course)
admin.site.register(models.ChallengeTaskQuestion)
admin.site.register(models.Prompt)
admin.site.register(models.Achievement)


class ChallengeTaskInline(admin.StackedInline):
    model = models.ChallengeTask


class ChallengeTaskQuestionInline(admin.TabularInline):
    model = models.ChallengeTaskQuestion


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


@admin.register(models.Habit)
class HabitAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


@admin.register(models.Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_select_related = ('client',)


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_select_related = ('client',)


@admin.register(models.DayResult)
class DayResultAdmin(admin.ModelAdmin):
    list_select_related = ('client',)


@admin.register(models.DailyCycle)
class DailyCycleAdmin(admin.ModelAdmin):
    list_select_related = ('client',)
    readonly_fields = ('created_at',)


@admin.register(models.Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    inlines = [ChallengeTaskInline]


@admin.register(models.ChallengeTask)
class ChallengeTaskAdmin(admin.ModelAdmin):
    inlines = [ChallengeTaskQuestionInline]
