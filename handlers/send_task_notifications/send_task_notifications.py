from aiogram import Dispatcher, Bot, Router, F
from database.Database import DataBase
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.send_task_notifications.keyboard import keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

send_task_router = Router()

db = DataBase()

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def send_message_current_time(bot: Bot, user_id: int, text: str, keyboard: keyboard):
    await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard)


# async def add_jobs(bot: Bot, processes):
#     if processes:
#         for process in processes:
#             text = f"Имя процесса: {process.process_name}\nОписание процесса: {process.action_description}"
#             scheduler.add_job(send_message_current_time, trigger='date',
#                               run_date=process.scheduled_time, name=f"{process.employee_id}-{process.process_name}",
#                               kwargs={'bot': bot, "user_id": process.employee.telegram_id,
#                                       "text": text, "keyboard": keyboard})
#
#         print(scheduler.get_jobs())
#         scheduler.start()
