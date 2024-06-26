from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def inline_today(last_tasks: List):
    keyboard = InlineKeyboardBuilder()
    for task in last_tasks:
        keyboard.add(InlineKeyboardButton(text=str(task), url='https'))
    return keyboard.adjust(1).as_markup()
