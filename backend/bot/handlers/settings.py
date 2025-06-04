from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.settings import settings_kb, to_settings_kb
from bot.keyboards.utils import keyboard_from_choices
from bot.states import SettingsState
from core.choices import UpgradeStyle, WeekDay
from core.models import Client, Profile

router = Router()


@router.callback_query(F.data == 'settings')
@flags.with_client
async def settings(query: CallbackQuery, client: Client):
    profile = await Profile.objects.aget(pk=client.pk)
    profile_info = profile.get_info('\n\n')
    await query.message.edit_text(
        f'Настройки\n\n{profile_info}\n'
        f'День еженедельного обзора: {WeekDay(client.week_report_day).label}',
        reply_markup=settings_kb,
    )


@router.callback_query(F.data.startswith('change_settings'))
async def change_settings(query: CallbackQuery, state: FSMContext):
    texts = {
        'month_goal': 'Напиши свою цель на следующие 30 дней.',
        'growth_zones': 'В каких сферах жизни ты хотел бы прокачаться?',
        'upgrade_style': 'Выбери стиль прокачки',
        'week_report_day': (
            'В какой день ты хочешь получать еженедельный отчет?'
        ),
    }

    field = query.data.split(':')[1]
    if field == 'upgrade_style':
        kb = keyboard_from_choices(UpgradeStyle)
    elif field == 'week_report_day':
        kb = keyboard_from_choices(WeekDay, adjust=2)
    else:
        kb = to_settings_kb

    await state.update_data(field=field)
    await state.set_state(SettingsState.change_settings)
    await query.message.edit_text(texts[field], reply_markup=kb)


@router.message(F.text, StateFilter(SettingsState.change_settings))
async def change_settings_message_handler(msg: Message, state: FSMContext):
    field = await state.get_value('field')
    await Profile.objects.filter(pk=msg.chat.id).aupdate(**{field: msg.text})

    await state.clear()
    await msg.answer('Настройки изменены!', reply_markup=to_settings_kb)


@router.callback_query(StateFilter(SettingsState.change_settings))
async def change_settings_callback_query_handler(
    query: CallbackQuery,
    state: FSMContext,
):
    client_id = query.message.chat.id
    field = await state.get_value('field')

    if field == 'upgrade_style':
        await Profile.objects.filter(pk=client_id).aupdate(
            upgrade_style=query.data,
        )
    else:
        await Client.objects.update_by_id(
            client_id,
            week_report_day=query.data,
        )

    await state.clear()
    await query.message.edit_text(
        'Настройки изменены!',
        reply_markup=to_settings_kb,
    )
