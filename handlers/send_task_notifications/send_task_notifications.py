from aiogram import Dispatcher, Bot, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from handlers.send_task_notifications.keyboard import keyboard
from aiogram.fsm.context import FSMContext

from database.Database import Database
from handlers.user_answer.states import WaitUserResponse
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


# @send_task_router.message(Command(WaitUserResponse.task_send))
# async def send_task(message: Message, state: FSMContext):
#     await state.set_state(WaitUserResponse.response)


async def start_send_task_notifications(bot: Bot, dp: Dispatcher, tasks):
    while True:
        await send_task_notifications(bot, tasks)
        await asyncio.sleep(3600)


def register_send_task_handlers(dp: Dispatcher, bot: Bot, tasks):
    asyncio.create_task(start_send_task_notifications(bot, dp, tasks))

# Работа с FSMContext. !!!!
