from django.db.models import TextChoices


class Priority(TextChoices):
    CALM = 'calm', 'Спокойствие'
    FOCUS = 'focus', 'Фокус'
    ACTION = 'action', 'Действие'


class SpendTime(TextChoices):
    MINUTES_5 = '5m', '5 минут'
    MINUTES_15 = '15m', '15 минут'
    MINUTES_30 = '30m', '30 минут'


class EnergyDirection(TextChoices):
    FUSS = 'fuss', 'Суета и хаос'
    PROCRASTINATION = 'procrastination', 'Прокрастинация'
    DOUBTS = 'doubts', 'Сомнения и самокопание'
    EMOTIONAL_SWING = 'emotional_swing', 'Эмоциональные качели'
    BURNOUT = 'burnout', 'Перегорание'
    STRUCTURE_ABSENCE = 'structure_absence', 'Отсутствие структуры'


class Purpose(TextChoices):
    CALM_INSIDE = 'calm_inside', 'Спокойствие внутри'
    ORDER_OF_ACTIONS = 'order_of_actions', 'Порядок в действиях'
    DISCIPLINE = 'discipline', 'Дисциплина'
    FOCUSING = 'focusing', 'Фокусировка'
    CONFIDENCE = 'confidence', 'Уверенность'


class SupportStyle(TextChoices):
    CALM = 'calm', 'Спокойный и поддерживающий'
    HARD = 'hard', 'Жёсткий и прямой'
    FLEXIBLE = 'flexible', 'Гибкий: поддержка + вызов'


class SupportOption(TextChoices):
    CALM_REMINDER = 'calm_reminder', 'Спокойное напоминание: ты можешь'
    DIRECT_CHALLENGE = 'direct_challenge', 'Прямой вызов: давай, соберись'
    QUESTION = 'question', 'Что ты чувствуешь и готов сделать?'


class UpgradeStyle(TextChoices):
    SOFT = 'soft', 'Мягкий'
    HARD = 'hard', 'Жёсткий'
    ADAPTIVE = 'adaptive', 'Адаптивный'


class ManifestType(TextChoices):
    CALM = 'calm', 'Спокойно'
    FOCUS = 'focus', 'С фокусом'
    PRESSURE = 'pressure', 'С напором'
    PACE = 'pace', 'С темпом'


class ScheduleType(TextChoices):
    BASIC = 'basic', 'Базовый'
    FOCUS = 'focus', 'Фокусный'
    HARD = 'hard', 'Жёсткий'


class PromptType(TextChoices):
    STATE_ANALYSIS = 'state_analysis', 'Анализ состояния'
    SELECT_MONTH_GOAL = 'select_month_goal', 'Выбор цели на 30 дней'
    MORNING_MESSAGE = 'morning_message', 'Утреннее сообщение'
    MORNING_EXTENDED_MESSAGE = (
        'morning_extended_message',
        'Утреннее сообщение (для платного тарифа)',
    )
    DAY_MESSAGE = 'day_message', 'Сообщение днем'
    EVENING_SUPPORT = 'evening_support', 'Сообщение-поддержка вечером'
    SELECT_OVERLOAD_METHOD = 'select_overload_method', 'SOS Кнопка'
    GET_SOS_HELP = 'get_sos_help', 'SOS Кнопка (для платного тарифа)'
    WEEK_REPORT = 'week_report', 'Еженедельный отчет'
    MONTH_REPORT = 'month_report', 'Ежемесячный отчет'


class AchievementType(TextChoices):
    CHALLENGE_COMPLETED = 'challenge_completed', 'Выполнение челленджа'
    CHALLENGE_TASKS_STREAK = (
        'challenge_tasks_streak',
        'Выполнение задач челленджа подряд',
    )
    SOS_BUTTON_USAGE = 'sos_button_usage', 'Использование SOS Кнопки'
    START_CHALLENGE = 'start_challenge', 'Начать челлендж'
    DAILY_CYCLES_STREAK = 'daily_cycles_streak', 'Вести дневник'
    BOT_USAGE = 'bot_usage', 'Использование бота'
    ACHIEVEMENTS_COLLECTION = 'achievements_collection', 'Получение достижений'
