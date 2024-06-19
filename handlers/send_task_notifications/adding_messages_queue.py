from aiogram import Bot, Router
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.send_task_notifications.keyboard import keyboard
import logging
from database.Database import DataBase, ProcessDB, EmployeesDB, ProcessStatus, EmployeeStatus

db = DataBase()
processDB = ProcessDB(db)
employeesDB = EmployeesDB(db)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

send_task_router = Router()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


def start_scheduler():
    if not scheduler.running:
        try:
            scheduler.start()
        except Exception as e:
            logger.warning("Ошибка при запуске scheduler .")


async def getting_employees_current_task(bot):
    all_waiting_processes = await processDB.get_all_waiting_to_be_sent_processes()
    for process in all_waiting_processes:
        await add_jobs(bot, process)


async def sent_message(bot: Bot, process):
    text = f"Имя процесса: {process.process_name}\nОписание процесса:{process.action_description}"
    print(text)
    employee = process.employee
    await processDB.change_status(process, status=ProcessStatus.sent)
    await employeesDB.change_status(employee=employee, status=EmployeeStatus.busy)

    await bot.send_message(chat_id=employee.telegram_id, text=text, reply_markup=keyboard)


async def add_jobs(bot, process):
    scheduler.add_job(sent_message, trigger='date', run_date=process.scheduled_time,
                      kwargs={"bot": bot, "process": process})
    start_scheduler()
