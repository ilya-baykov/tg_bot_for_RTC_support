import datetime

from aiogram import Bot, Router
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.send_task_notifications.keyboard import keyboard
import logging
from database.Database import DataBase, ProcessDB, EmployeesDB, ProcessStatus, EmployeeStatus

from global_variables import bot
from handlers.sheduler import scheduler

db = DataBase()
processDB = ProcessDB(db)
employeesDB = EmployeesDB(db)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

send_task_router = Router()


def start_scheduler():
    if not scheduler.running:
        try:
            scheduler.start()
            print(f"Запускаем работу шедулера {scheduler}")
        except Exception as e:
            logger.warning("Ошибка при запуске scheduler .")


async def getting_employees_current_task():
    all_waiting_processes = await processDB.get_all_waiting_to_be_sent_processes()
    for process in all_waiting_processes:
        print(f"Процесс: {process.process_name} был добавлен в планировшик")
        await add_jobs(bot, process)


async def sent_message(bot: Bot, process):
    text = f"Имя процесса: {process.process_name}\nОписание процесса:{process.action_description}"
    print(text)
    employee = process.employee
    await processDB.change_status(process, status=ProcessStatus.sent)
    await employeesDB.change_status(employee=employee, status=EmployeeStatus.busy)

    await bot.send_message(chat_id=employee.telegram_id, text=text, reply_markup=keyboard)


async def add_jobs(bot, process):
    current_time = datetime.datetime.now()
    scheduled_time = process.scheduled_time

    if current_time > scheduled_time:
        scheduled_time = current_time + datetime.timedelta(seconds=5)
        await processDB.change_scheduled_time(process, scheduled_time)

    scheduler.add_job(sent_message, trigger='date', run_date=scheduled_time,
                      kwargs={"bot": bot, "process": process})
    start_scheduler()
