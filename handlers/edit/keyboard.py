from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.CRUD.read import InputTableReader


class TaskInfo(CallbackData, prefix="task_info_inline_kb"):
    task_id: str


async def inline_today(last_tasks: List):
    keyboard = InlineKeyboardBuilder()
    for action_today_task in last_tasks:
        input_task = await InputTableReader().get_input_task_by_id(action_today_task.input_data_id)
        callback_data = TaskInfo(task_id=str(action_today_task.id))
        keyboard.add(InlineKeyboardButton(text=f"{input_task.process_name}:{input_task.action_description}",
                                          callback_data=callback_data.pack()))
    return keyboard.adjust(1).as_markup()
