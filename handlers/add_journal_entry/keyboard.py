from aiogram.utils.keyboard import ReplyKeyboardBuilder

SENT_BUTTON_TEXT = "Отправить"
BACK_BUTTON_TEXT = "Назад"
EXIT_BUTTON_TEXT = "Выход"


def add_journal_log_kb(back_button: bool = False, exit_button: bool = False, sent_button: bool = False):
    builder = ReplyKeyboardBuilder()
    if back_button: builder.button(text="Назад")
    if sent_button: builder.button(text="Отправить")
    if exit_button: builder.button(text="Завершение заполнения формы (Выход)")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True,
                             input_field_placeholder="Нажмите на одну из кнопок",
                             one_time_keyboard=True)
