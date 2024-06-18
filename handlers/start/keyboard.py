from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Создаём клавиатуру
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить свой контакт", request_contact=True)
        ]

    ],
    resize_keyboard=False,
    one_time_keyboard=True,
    input_field_placeholder="Нажми на клавишу для отправки своего контакта"
)
