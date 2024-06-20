import logging

from sqlalchemy import select, asc

from main_objects import db
from database.models import *
from exeptions import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmployeesReader:

    async def get_employee_by_telegram_id_or_username(self, telegram_id: str | None = None,
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


class InputTableReader:
    async def get_all_actions(self):
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
