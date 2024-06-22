import logging
import calendar

from datetime import date

from database.CRUD.update import EmployeesUpdater
from run_app.main_objects import db
from database.models import *
from database.CRUD.read import EmployeesReader, InputTableReader, ActionsTodayReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

employees_reader = EmployeesReader()
input_table_reader = InputTableReader()
employees_updater = EmployeesUpdater()
actions_today_reader = ActionsTodayReader()


class EmployeesCreator:
    @staticmethod
    async def create_new_employees(name: str | None, telegram_username: str, telegram_id: str | int):
        """Добавляем / Регистрируем нового сотрудника или изменяем username у текущего сотрудника """
        async with db.Session() as request:
            employee = await employees_reader.get_employee_by_telegram_id_or_username(telegram_id=str(telegram_id))
            if employee:
                # Если сотрудник изменил username - заменяем значение в таблице
                if employee.telegram_username != telegram_username:
                    employee.telegram_username = telegram_username
                    await request.commit()
                    logger.info(f"Telegram username для telegram_id '{telegram_id}' обновлен на '{telegram_username}'.")
                else:
                    logger.info(f"Пользователь с telegram_id '{telegram_id}' уже существует и не требует обновления.")
            else:
                # Создать нового сотрудника
                request.add(Employees(
                    name=name,
                    telegram_username=telegram_username,
                    telegram_id=telegram_id,
                ))
                logger.info(f"Пользователь с telegram_id '{telegram_id}' добавлен в таблицу employees.")

                await request.commit()


class ActionsTodayCreator:

    @staticmethod
    async def create_new_actions():
        """Формируем актуальные задачи из исходной таблицы """
        async with db.Session() as session:
            tasks = await input_table_reader.get_all_actions()  # Получаем список всех задач из входной таблицы
            busy_employees = {}  # Словарь 'занятых' сотрудников

            for task in tasks:
                if await ActionsTodayCreator.is_perform_today(day_of_action=task.completion_day):
                    await ActionsTodayCreator.process_task(task, busy_employees, session)

    @staticmethod
    async def create_action(task, employee, status, session):
        """Создание новой задачи"""
        session.add(ActionsToday(
            input_data_id=task.id,
            employee_id=employee.id,
            status=status
        ))
        await session.commit()
        logger.info(f"Задача {task.process_name} была добавлена со статусом {status}")

    @staticmethod
    async def is_perform_today(day_of_action: str | None) -> bool:
        # Если день выполнения не указан - выполнять каждый день
        if day_of_action is None:
            return True

        today_date = date.today()  # Получаем текущую дату
        if day_of_action == "последний":
            # Получаем количество дней в этом месяце
            last_day_month = calendar.monthrange(today_date.year, today_date.month)[1]
            return int(day_of_action) == last_day_month

        return int(day_of_action) == today_date.day

    @staticmethod
    async def process_task(task, busy_employees, session):
        """Обрабатываем задачу"""
        if await ActionsTodayCreator.is_task_already_created(task):
            logger.info(f"Задача {task.id} уже была создана.")
            return

        employee, status = await ActionsTodayCreator.assign_employee_and_status(task, busy_employees)
        if not employee:
            logger.warning(f"Сотрудник с telegram_username '{task.telegram_username}' не найден.")
            return

        await ActionsTodayCreator.create_action(task, employee, status, session)

    @staticmethod
    async def is_task_already_created(task):
        """Проверка наличия задачи в таблице actions"""
        return await actions_today_reader.get_action(task.id) is not None

    @staticmethod
    async def assign_employee_and_status(task, busy_employees):
        """Назначение сотрудника и статуса задачи"""
        if task.telegram_username in busy_employees:
            employee = busy_employees[task.telegram_username]
            status = ActionStatus.queued_to_be_added
        else:
            employee = await employees_reader.get_employee_by_telegram_id_or_username(task.telegram_username)
            if not employee:
                logger.warning(f"Сотрудник с telegram_username '{task.telegram_username}' не найден.")
                return None, None

            busy_employees[task.telegram_username] = employee
            status = await ActionsTodayCreator.determine_status(employee)

        return employee, status

    @staticmethod
    async def determine_status(employee):
        """Определение статуса задачи на основе количества задач у сотрудника"""
        tasks_count = await employees_reader.get_all_employee_tasks(employee.id)
        return ActionStatus.queued_to_be_added if len(tasks_count) > 0 else ActionStatus.waiting_to_be_sent


class ReportCreator:
    @staticmethod
    async def create_new_report(action_id: int, employee_id: int, expected_dispatch_time: datetime.datetime,
                                actual_dispatch_time: datetime.datetime, employee_response_time: datetime.datetime,
                                elapsed_time: datetime.timedelta, status: FinalStatus, comment: str):
        async with db.Session() as request:
            request.add(Report(
                action_id=action_id,
                employee_id=employee_id,
                expected_dispatch_time=expected_dispatch_time,
                actual_dispatch_time=actual_dispatch_time,
                employee_response_time=employee_response_time,
                elapsed_time=elapsed_time,
                status=status,
                comment=comment
            ))
            await request.commit()
            logger.info(f"Добавлена запись в отчетную таблицу. № Действия {action_id} со статусом {status}")
