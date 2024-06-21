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

        async  with db.Session() as request:
            if telegram_id is None and telegram_username is None:
                raise TelegramIdOrUsernameError("Необходимо задать telegram_id или telegram_username")

            # Выполняем запрос с использованием фильтра
            if telegram_id:
                query = select(Employees).filter_by(telegram_id=telegram_id)  # Поиск по telegram_id
            else:
                query = select(Employees).filter_by(telegram_username=telegram_username)  # Поиск по telegram_username

            result = await request.execute(query)
            employee = result.scalar_one_or_none()

            logger.info(f"Найден сотрудник: {employee.name}")
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
