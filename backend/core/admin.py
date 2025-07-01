from django.contrib import admin
from django.contrib.auth.models import Group

from bot.config import config
from core import models
from core.models import PromoCode

admin.site.unregister(Group)

admin.site.register(models.Course)
admin.site.register(models.ChallengeTaskQuestion)
admin.site.register(models.Prompt)
admin.site.register(models.Achievement)
admin.site.register(models.SubscriptionPrice)


class ChallengeTaskInline(admin.StackedInline):
    model = models.ChallengeTask


class ChallengeTaskQuestionInline(admin.TabularInline):
    model = models.ChallengeTaskQuestion


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    list_filter = ('start_promo_code',)


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


@admin.register(models.PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'promo_url')

    def promo_url(self, obj):
        return f'{config.BOT_LINK}?start={obj.code}'

    promo_url.short_description = 'Ссылка'


@admin.register(models.PromoCodeActivation)
class PromoCodeActivationAdmin(admin.ModelAdmin):
    readonly_fields = ('client', 'promo_code', 'date',)
    list_select_related = ('client', 'promo_code')
