from aiogram import Bot, Router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.send_task_notifications.keyboard import keyboard
import logging

from database.Database import DataBase, ProcessDB, ProcessStatus

db = DataBase()
processDB = ProcessDB(db)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

send_task_router = Router()

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
scheduler.start()


async def getting_employees_current_task(bot: Bot):
    all_waiting_processes = await processDB.get_all_waiting_to_be_sent_processes()
    for process in all_waiting_processes:
        await add_jobs(bot=bot, process=process, employee_id=process.employee_id)
    # Для каждого сотрудника захватить первую в очереди задачу
    # У сотрудника поменять статус
    # вызвыть функцию add_jobs


async def send_message_current_time(bot: Bot, process, user_id: int, text: str, keyboard: keyboard):
    process.status = ProcessStatus.sent
    # Изменить статус задачи на "Отправлено"
    await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard)


async def add_jobs(bot: Bot, process, employee_id):
    text = f"Имя процесса: {process.process_name}\nОписание процесса: {process.action_description}"
    print(text)
    scheduler.add_job(send_message_current_time, trigger='date',
                      run_date=process.scheduled_time, name=f"{process.employee_id}-{process.process_name}",
                      kwargs={'bot': bot, "process": process, "user_id": process.employee.telegram_id,
                              "text": text, "keyboard": keyboard})
