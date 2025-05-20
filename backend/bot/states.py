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
