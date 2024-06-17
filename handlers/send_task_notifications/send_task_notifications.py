from aiogram import Dispatcher, Bot, Router, F
from database.Database import Database
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

send_task_router = Router()

db = Database()

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def send_message_current_time(bot: Bot, user_id: int, text="Привет, это провекра отправки сообщения"):
    await bot.send_message(user_id, text)


#
# scheduler.add_job(send_message_current_time, trigger='date',
#                   run_date=datetime.datetime.now() + datetime.timedelta(seconds=10), kwargs={'bot': bot})

async def add_jobs(bot: Bot, processes):
    for process in processes:
        print(process.employee.telegram_id)
        print(process.scheduled_time)
        print(process.action_description)
        scheduler.add_job(send_message_current_time, trigger='date',
                          run_date=process.scheduled_time,
                          kwargs={'bot': bot, "user_id": process.employee.telegram_id,
                                  "text": process.action_description})
    scheduler.start()
