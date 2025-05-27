from bot.keyboards.utils import one_button_keyboard


def get_greeting_kb(text: str):
    return one_button_keyboard(text=text, callback_data='start_survey')
