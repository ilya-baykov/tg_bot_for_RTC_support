from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TaskInfo(CallbackData, prefix="task_info_inline_kb"):
    task_id: str


async def inline_today(last_tasks: List):
    keyboard = InlineKeyboardBuilder()
    last_tasks = last_tasks[:3]  # Получаем последние 3 задачи
    for today_report in last_tasks:
        callback_data = TaskInfo(task_id=str(today_report.id))
        keyboard.add(InlineKeyboardButton(text=f"{today_report.process_name}",
                                          callback_data=callback_data.pack()))
    return keyboard.adjust(1).as_markup()
