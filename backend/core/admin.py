from django.contrib import admin
from django.contrib.auth.models import Group

from core import models

admin.site.unregister(Group)


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
