import asyncio
import logging
from turtle import delay

from aiogram.exceptions import TelegramAPIError
from database.CRUD.read import InputTableReader, EmployeesReader
from database.CRUD.update import ActionsTodayUpdater
from database.CRUD.сreate import employees_updater
from database.enums import IntervalType, EmployeesStatus, ActionStatus
from datetime import datetime, timedelta

from database.models import ActionsToday, InputData
from run_app.main_objects import bot
from sent_task_to_emploeyee.keyboard import keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

actions_today_updater = ActionsTodayUpdater()
employees_reader = EmployeesReader()


def check_scheduler(scheduler):
    if not scheduler.running:
        scheduler.start()
        logger.info(f"Планировщик заданий {scheduler} запущен")
    else:
        logger.info("Планировщик уже был запущен")


async def add_task_scheduler(scheduler, action_task: ActionsToday):
    check_scheduler(scheduler)
    input_data_task = await InputTableReader().get_input_task_by_id(action_task.input_data_id)
    scheduled_time = input_data_task.scheduled_time

    # Преобразуем время в объекты datetime
    scheduled_datetime = datetime.combine(datetime.today(), scheduled_time)
    current_datetime = datetime.now()

    # Увеличиваем текущее время на 5 секунд, если текущее время больше запланированного
    if current_datetime > scheduled_datetime:
        scheduled_datetime = current_datetime + timedelta(seconds=5)
        scheduled_time = scheduled_datetime.time()
        logger.info(
            f"Время отправки действия: №{action_task.id} было изменено с {input_data_task.scheduled_time}"
            f" на scheduled_time")

    # Обновляем время отправки сообщения
    await actions_today_updater.update_actual_time_message(action=action_task, time=scheduled_time)

    logger.info(f"Действие: №{action_task.id} был добавлен в планировшик. Время выполнения: {scheduled_time}")
    scheduler.add_job(sent_message_with_retry, trigger='date', run_date=scheduled_datetime,
                      kwargs={"action_task": action_task, "input_data_task": input_data_task})


async def sent_message_with_retry(action_task: ActionsToday, input_data_task: InputData, retries=3, delay=5):
    try:
        await sent_message(action_task, input_data_task)
    except TelegramAPIError as e:
        logger.error(f"Ошибка отправки сообщения для действия: №{action_task.id}, ошибка: {e}")
        if retries > 0:
            logger.info(f"Повторная попытка отправки сообщения для действия: №{action_task.id} через {delay} секунд")
            await asyncio.sleep(delay)
            await sent_message_with_retry(action_task, input_data_task, retries - 1, delay * 2)
        else:
            logger.error(f"Не удалось отправить сообщение для действия: №{action_task.id} после нескольких попыток")


async def sent_message(action_task: ActionsToday, input_data_task: InputData):
    message_text = f"Имя процесса: {input_data_task.process_name}\nОписание процесса:{input_data_task.action_description}"
    employee = await employees_reader.get_employee_by_id(action_task.employee_id)

    logger.info(f"{message_text} Было отправлено пользователю {employee.id}")

    await bot.send_message(chat_id=employee.telegram_id, text=message_text, reply_markup=keyboard)

    # Если сообщение было отправлено успешно, обновляем статус действия и сотрудника
    await actions_today_updater.update_status(action_task, ActionStatus.sent)  # Изменить статус действия
    await employees_updater.update_status(employee, EmployeesStatus.busy)  # Изменяем статус сотрудника
