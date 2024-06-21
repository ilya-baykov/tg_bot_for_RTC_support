import logging
from typing import List

from sqlalchemy import select, asc

from main_objects import db
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
    async def get_all_employee_tasks(employee_id: int) -> List:
        """Возвращает все текущие задачи сотрудника"""
        async with db.Session() as request:
            query = select(Actions).filter_by(employee_id=employee_id)
            result = await request.execute(query)
            tasks = result.scalars().all()
            logger.info(f"У сотрудника {employee_id} найдены такие задачи : {[task.id for task in tasks]}")
            return tasks


class InputTableReader:
    @staticmethod
    async def get_all_actions():
        """Возвращает список всех действий из исходной таблицы"""

        async with (db.Session() as request):
            query = (

                select(InputData)
                .filter(InputData.scheduled_time > datetime.datetime.now())
                .order_by(asc(InputData.scheduled_time))

            )
            result = await request.execute(query)
            tasks = result.scalars().all()

            logger.info(f"Найденные актуальные задачи: {[task.process_name for task in tasks]}")
            return tasks

    @staticmethod
    async def get_input_task_by_id(input_data_id: int):
        async with db.Session() as request:
            query = select(InputData).filter_by(id=input_data_id)
            result = await request.execute(query)
            input_data_task = result.scalar_one_or_none()
            if input_data_task:
                logger.info(f"По ID:{input_data_id} получена задача {input_data_task.process_name}")
            else:
                logger.info(f"По ID:{input_data_id} не найдено задач")
            return input_data_task


class ActionsReader:
    @staticmethod
    async def get_action(input_data_id: int):
        """Получаем действия по идентификатору входной таблицы"""
        async with db.Session() as request:
            query = select(Actions).filter_by(input_data_id=input_data_id)
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
            query = select(Actions).filter_by(status=ActionStatus.waiting_to_be_sent)
            result = await request.execute(query)
            tasks = result.scalars().all()
            logger.info(f"Действия ожидающие отправки:{[task.id for task in tasks]}")
            return tasks
