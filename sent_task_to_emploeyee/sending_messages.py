import logging

from database.CRUD.read import InputTableReader, EmployeesReader
from database.CRUD.update import ActionsUpdater
from database.CRUD.сreate import employees_updater
from database.enums import IntervalType, EmployeesStatus, ActionStatus
from datetime import datetime, timedelta

from database.models import Actions, InputData
from run_app.main_objects import bot
from sent_task_to_emploeyee.keyboard import keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

actions_updater = ActionsUpdater()
employees_reader = EmployeesReader()


async def add_task_scheduler(scheduler, action_task: Actions):
    input_data_task = await InputTableReader().get_input_task_by_id(action_task.input_data_id)
    interval_type = input_data_task.interval

    if interval_type == IntervalType.разово:
        current_time = datetime.now()
        scheduled_time = input_data_task.scheduled_time

        if current_time > scheduled_time:
            scheduled_time = current_time + timedelta(seconds=5)

            logger.info(
                f"Время отправки действия: №{action_task.id} было изменено с {input_data_task.scheduled_time}"
                f" на {scheduled_time}")

        # Обновляем время отправки сообщения
        await actions_updater.update_actual_time_message(action=action_task, time=scheduled_time)

        logger.info(f"Действие: №{action_task.id} был добавлен в планировшик. Время выполнения: {scheduled_time}")
        scheduler.add_job(sent_message, trigger='date', run_date=scheduled_time,
                          kwargs={"action_task": action_task, "input_data_task": input_data_task})
    # elif Если тип интервала - ежедневно:
    #     pass
    # elif Если тип интервала - ежемесячно:
    #      pass


async def sent_message(action_task: Actions, input_data_task: InputData):
    message_text = f"Имя процесса: {input_data_task.process_name}\nОписание процесса:{input_data_task.action_description}"
    employee = await employees_reader.get_employee_by_id(action_task.employee_id)
    await actions_updater.update_status(action_task, ActionStatus.sent)  # Изменить статус действия
    await employees_updater.update_status(employee, EmployeesStatus.busy)  # Изменяем статус сотрудника

    logger.info(f"{message_text} Быдл отправлено пользователю {employee.id}")
    await bot.send_message(chat_id=employee.telegram_id, text=message_text, reply_markup=keyboard)
