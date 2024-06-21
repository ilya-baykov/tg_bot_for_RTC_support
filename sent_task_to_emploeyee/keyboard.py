from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Создаём клавиатуру
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выполнено"), KeyboardButton(text="Не выполнено")],
    ],
    resize_keyboard=False,
    one_time_keyboard=True
)
