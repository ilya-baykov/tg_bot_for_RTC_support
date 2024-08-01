from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

yes_or_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Да"),
            KeyboardButton(text="Нет")
        ]

    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Нажми на одну из клавиш"
)
