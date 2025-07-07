from aiogram import F, Router, flags
from aiogram.types import CallbackQuery

from bot.keyboards.start import back_to_start_kb
from core.models import (
    Client,
    ClientAchievement,
    ClientChallenge,
    ClientChallengeTaskQuestion,
    ClientSosButtonUsage,
    DailyCycle,
)

router = Router()


@router.callback_query(F.data == 'achievements')
@flags.with_client(only_subscribers=True)
async def achievements_handler(query: CallbackQuery, client: Client):
    completed_challenges = await ClientChallenge.objects.get_completed_count(
        client.pk,
    )
    tasks_streak = await ClientChallengeTaskQuestion.objects.get_streak(
        client.pk,
    )
    sos_button_usages = await ClientSosButtonUsage.objects.get_usages(
        client.pk,
    )
    started_challenges = await ClientChallenge.objects.get_started_count(
        client.pk,
    )
    cycles_count = await DailyCycle.objects.get_count(client.pk)
    achievements_count = await ClientAchievement.objects.get_count(client.pk)

    return query.message.edit_text(
        'Твои достижения:\n'
        f'Начато челленджей: {started_challenges}\n'
        f'Пройдено челленджей: {completed_challenges}\n'
        f'Выполнения заданий челленджей подряд: {tasks_streak}\n'
        f'Использования SOS Кнопки: {sos_button_usages}\n'
        f'Записей в дневнике: {cycles_count}\n'
        f'Заработано достижений: {achievements_count}',
        reply_markup=back_to_start_kb,
    )
