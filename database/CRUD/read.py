import datetime
import logging
from typing import List

from sqlalchemy import select, asc

from run_app.main_objects import db
from database.models import *
from exeptions import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmployeesReader:

    @staticmethod
    async def get_employee_by_telegram_id_or_username(telegram_id: str | None = None,
                                                      telegram_username: str | None = None):
        """Возвращает объект сотрудника"""

        async with db.Session() as request:
            if telegram_id is None and telegram_username is None:
                raise TelegramIdOrUsernameError("Необходимо задать telegram_id или telegram_username")

            # Выполняем запрос с использованием фильтра
            if telegram_id:
                query = select(Employees).filter_by(telegram_id=telegram_id)  # Поиск по telegram_id
            else:
                query = select(Employees).filter_by(telegram_username=telegram_username)  # Поиск по telegram_username

            result = await request.execute(query)
            employee = result.scalar_one_or_none()
            if employee:
                logger.info(f"Найден сотрудник: {employee.name}")
            else:
                logger.info(f"Сотрудник не найден. Поиск по {telegram_id}, {telegram_username} ")
            return employee

    @staticmethod
    async def get_employee_by_phone(phone_number: str):
        """Возвращает объект сотрудника (модели Employees) по его номеру телефона"""
        async with db.Session() as request:
            query = select(EmployeesContact).filter_by(phone_number=phone_number)
            result = await request.execute(query)
            employee = result.scalar_one_or_none()
            if employee:
                logger.info(
                    f"По номеру телефона: {phone_number} был найден сотрудник №{employee.id} - {employee.fullname}")
            else:
                logger.info(f"По номеру телефона: {phone_number} не было найдено сотрудников")

            return employee

    @staticmethod
    async def get_employee_by_id(employee_id: int):
        """Возвращает объект сотрудника (модели Employees) по его id"""
        async with db.Session() as request:
            query = select(Employees).filter_by(id=employee_id)
            result = await request.execute(query)
            employee = result.scalar_one_or_none()
            if employee:
                logger.info(f"По Первичному ключу: {employee_id} получен сотрудник {employee.name}")
            else:
                logger.info(f"По Первичному ключу: {employee_id} не был найден  сотрудник")

            return employee

    @staticmethod
    async def get_all_employee_tasks(employee_id: int) -> List:
        """Возвращает все текущие задачи сотрудника"""
        async with db.Session() as request:
            query = select(ActionsToday).filter_by(employee_id=employee_id)
            result = await request.execute(query)
            tasks = result.scalars().all()
            logger.info(f"У сотрудника {employee_id} найдены такие задачи : {[task.id for task in tasks]}")
            return tasks


class ClearInputTableReader:
    @staticmethod
    async def get_all_actions():
        """Возвращает список всех действий из исходной таблицы"""

        async with (db.Session() as request):
            query = (

                select(ClearInputData)
                .filter(ClearInputData.scheduled_time > datetime.datetime.now().time())
                .order_by(asc(ClearInputData.scheduled_time), asc(ClearInputData.id))

            )
            result = await request.execute(query)
            tasks = result.scalars().all()

            logger.info(f"Найденные актуальные задачи: {[task.process_name for task in tasks]}")
            return tasks

    @staticmethod
    async def get_input_task_by_id(input_data_id: int):
        async with db.Session() as request:
            query = select(ClearInputData).filter_by(id=input_data_id)
            result = await request.execute(query)
            input_data_task = result.scalar_one_or_none()
            if input_data_task:
                logger.info(f"По ID:{input_data_id} получена задача {input_data_task.process_name}")
            else:
                logger.info(f"По ID:{input_data_id} не найдено задач")
            return input_data_task


class ActionsTodayReader:
    @staticmethod
    async def get_action(input_data_id: int):
        """Получаем действия по идентификатору входной таблицы"""
        async with db.Session() as request:
            query = select(ActionsToday).filter_by(input_data_id=input_data_id)
            result = await request.execute(query)
            task = result.scalar_one_or_none()
            if task:
                logger.info(f"По ключу входной таблицы {input_data_id} получена задача {task.id}")
            else:
                logger.info(f"По ключу входной таблицы {input_data_id} не было получено задач")
            return task

    @staticmethod
    async def get_pending_actions() -> List:
        """Возвращает список всех действий, ожидающих отправки сообщения """
        async with db.Session() as request:
            query = select(ActionsToday).filter_by(status=ActionStatus.waiting_to_be_sent)
            result = await request.execute(query)
            tasks = result.scalars().all()
            logger.info(f"Действия ожидающие отправки:{[task.id for task in tasks]}")
            return tasks

    @staticmethod
    async def get_submitted_task_by_employee_id(employee_id: int):
        """Возвращает список всех действий сотрудника со статусом 'отправлено' """
        async with db.Session() as request:
            query = (
                select(ActionsToday)
                .filter_by(employee_id=employee_id, status=ActionStatus.sent)
            )
            result = await request.execute(query)
            sent_task = result.scalar_one_or_none()

            if sent_task:
                logger.info(f"У сотрудника №: {employee_id} есть действие со статусом 'Отправлено' - №{sent_task}")
            else:
                logger.info(f"У сотрудника №: {employee_id} нет действий со статусом 'Отправлено'")

            return sent_task

    @staticmethod
    async def get_queued_to_be_added_actions_by_employee_id(employee_id) -> List:
        """Возвращает все задачи сотрудника со статусом 'В очереди на добавление в обработку' """
        async with db.Session() as request:
            query = (
                select(ActionsToday)
                .join(ClearInputData, ActionsToday.input_data_id == ClearInputData.id)
                .filter(ActionsToday.employee_id == employee_id, ActionsToday.status == ActionStatus.queued_to_be_added)
                .order_by(asc(ClearInputData.scheduled_time))
            )
            result = await request.execute(query)
            actions = result.scalars().all()
            logger.info(f"У сотрудника №{employee_id} есть такие задачи в очереди: {[action.id for action in actions]}")
            return actions

    @staticmethod
    async def get_completed_actions_by_employee_id(employee_id) -> List:
        """Возвращает все задачи сотрудника со статусом completed """
        async with db.Session() as request:
            query = (
                select(ActionsToday)
                .join(ClearInputData, ActionsToday.input_data_id == ClearInputData.id)
                .filter(ActionsToday.employee_id == employee_id, ActionsToday.status == ActionStatus.completed)
                .order_by(asc(ClearInputData.scheduled_time))
            )
            result = await request.execute(query)
            actions = result.scalars().all()
            logger.info(f"У сотрудника №{employee_id} есть такие задачи в очереди: {[action.id for action in actions]}")
            return actions


class UserAccessReader:
    @staticmethod
    async def get_user(telegram_id: str) -> UserAccess | None:
        """Возвращает пользователя из таблицы user_access или None"""
        async with db.Session() as request:
            query = select(UserAccess).filter_by(telegram_id=telegram_id)
            result = await request.execute(query)
            user = result.scalar_one_or_none()
            return user

    @staticmethod
    async def is_block_user(telegram_id: str) -> UserAccess | None:
        """Проверяет статус пользователя (заблокирован или нет)"""
        async with db.Session() as request:
            query = select(UserAccess).filter_by(telegram_id=telegram_id, user_status=UserStatus.blocked)
            result = await request.execute(query)
            verdict = result.scalar_one_or_none()
            return verdict


class SchedulerTasksReader:
    @staticmethod
    async def get_tasks(scheduler_task_id: str) -> SchedulerTasks | None:
        """Возаращвает задачу из scheduler_tasks"""
        async with db.Session() as request:
            query = select(SchedulerTasks).filter_by(id=scheduler_task_id)
            result = await request.execute(query)
            task = result.scalar_one_or_none()
            return task

    @staticmethod
    async def get_last_task_by_employee(employee_id: int) -> SchedulerTasks | None:
        """Возвращает последнюю задачу конкретного сотрудника со статусом awaiting_dispatch"""
        async with db.Session() as request:
            query = (
                select(SchedulerTasks)
                .filter_by(employee_id=employee_id, status=SchedulerStatus.awaiting_dispatch)
                .order_by(asc(SchedulerTasks.expected_completion_time))

            )
            result = await request.execute(query)
            return result.scalar_one_or_none()


class ReportReader:
    @staticmethod
    async def get_report_by_actions_id(task_id: int) -> Report | None:
        """Возвращает строку из таблицы report_table"""
        async with db.Session() as request:
            query = select(Report).filter_by(action_id=task_id)
            result = await request.execute(query)
            report = result.scalar_one_or_none()
            return report


class RawInputTable:
    @staticmethod
    async def get_row_table_data() -> List[RawInputData]:
        """Считывает все строки из необработанной входной таблицы"""
        async with db.Session() as request:
            query = select(RawInputData)
            result = await request.execute(query)
            data = result.scalars().all()
            logger.info(f"В исходной таблице {len(data)} строк")
            return data
