from typing import List
from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Report


class TaskInfo(CallbackData, prefix="task_info_inline_kb"):
    task_id: str


async def inline_today(last_tasks: List[Report]):
    inline_keyboard = InlineKeyboardBuilder()
    last_tasks = last_tasks[:3]  # Получаем последние 3 задачи
    for today_report in last_tasks:
        callback_data = TaskInfo(task_id=str(today_report.id))
        inline_keyboard.add(InlineKeyboardButton(text=f"{today_report.process_name}:{today_report.action_description}",
                                                 callback_data=callback_data.pack()))
    return inline_keyboard.adjust(1).as_markup()


# Создаём Reply-клавиатуру
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выполнено"), KeyboardButton(text="Не выполнено")]],
    resize_keyboard=True,
    one_time_keyboard=True
)
