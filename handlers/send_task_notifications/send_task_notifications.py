from aiogram import Dispatcher, Bot, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.send_task_notifications.keyboard import keyboard

from database.Database import Database

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

send_task_router = Router()

db = Database()


async def send_task_notifications(bot: Bot, tasks):
    try:
        for task in tasks:
            employee = await db.get_employee_by_telegram_username(task.employee_telegram)
            if employee:
                process = await db.get_process_by_name(task.process_name)
                if process:
                    message_text = (
                        f"Привет, {employee.name}!\n"
                        f"Ваша задача: {process.process_name}\n"
                        f"Описание: {process.action_description}\n"
                        f"Запланировано на: {task.scheduled_time}"
                    )
                    try:
                        await bot.send_message(chat_id=employee.telegram_id, text=message_text, reply_markup=keyboard)

                        logger.info(f"Отправлено уведомление о задаче для сотрудника {employee.name}")
                    except Exception as e:
                        logger.error(f"Ошибка при отправке уведомления для сотрудника {employee.name}: {e}")
    except Exception as e:
        logger.error(f"Ошибка при получении задач из базы данных: {e}")


async def start_send_task_notifications(bot: Bot, dp: Dispatcher, tasks):
    while True:
        await send_task_notifications(bot, tasks)
        await asyncio.sleep(3600)  # Отправлять уведомления каждый час


def register_send_task_handlers(dp: Dispatcher, bot: Bot, tasks):
    asyncio.create_task(start_send_task_notifications(bot, dp, tasks))
