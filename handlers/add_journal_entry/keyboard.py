from aiogram.utils.keyboard import ReplyKeyboardBuilder

SENT_BUTTON_TEXT = "Отправить"
BACK_BUTTON_TEXT = "Назад"
EXIT_BUTTON_TEXT = "Выход"


def add_journal_log_kb(back_button: bool = True, exit_button: True = True, sent_button: bool = False,
                       error_types: bool = False):
    builder = ReplyKeyboardBuilder()
    if error_types:
        builder.button(text="Инфраструктурная ошибка")
        builder.button(text="Бизнес ошибка")
        builder.button(text="Ошибка робота")
        builder.button(text="Ошибка запуска")
        builder.button(text="Нет значения")
    if back_button: builder.button(text=BACK_BUTTON_TEXT)
    if sent_button: builder.button(text=SENT_BUTTON_TEXT)
    if exit_button: builder.button(text=EXIT_BUTTON_TEXT)
    builder.adjust(2, 3, 2) if error_types else builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True,
                             input_field_placeholder="Нажмите на одну из кнопок",
                             one_time_keyboard=True)


