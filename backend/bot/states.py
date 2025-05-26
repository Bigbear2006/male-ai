from aiogram.fsm.state import State, StatesGroup


class SubscriptionState(StatesGroup):
    buying = State()


class SurveyState(StatesGroup):
    preferred_name = State()
    age = State()
    shape = State()
    last_forces_source = State()
    self_rating = State()
    energy_directions = State()
    purpose = State()
    future_version = State()
    support_style = State()
    support_option = State()
    key_quality = State()


class ProfileState(StatesGroup):
    month_goal = State()
    growth_zones = State()
    upgrade_style = State()


class HabitState(StatesGroup):
    add = State()
    update = State()


class DayResultState(StatesGroup):
    result = State()


class DailyCycleState(StatesGroup):
    morning_wellbeing = State()
    success_result = State()
    fail_result = State()
    feelings = State()
    evening_wellbeing = State()


class ScheduleState(StatesGroup):
    time_block_name = State()
    time_block_start = State()
    time_block_end = State()
    time_block_edit = State()


class SosButtonState(StatesGroup):
    problem = State()


class ChallengeState(StatesGroup):
    answer_task_questions = State()
