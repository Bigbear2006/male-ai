from core.models import Survey


def state_analysis_prompt(survey: Survey):
    return (
        f'Проанализируй состояние человека по следующим данным:\n'
        f'{survey.info}\n\n'
        f'ВАЖНО:'
        f'Обращайся прямо к этому человеку.\n'
        f'Не нужно ставить ** и ###'
    )


def select_month_goal_prompt(survey: Survey):
    return (
        f'Предложи цель на месяц по следующим данным:\n'
        f'{survey.info}'
        f'ВАЖНО:\n'
        f'Сформулируй цель, не надо расписывать шаги.\n'
        f'Не нужно писать само слово цель и двоеточие в начале.\n'
        f'Не нужно ставить ** и ###'
    )
