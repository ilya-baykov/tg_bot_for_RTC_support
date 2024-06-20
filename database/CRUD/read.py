from sqlalchemy import select

from main_objects import db
from database.models import *
from exeptions import *


class EmployeesReader:

    async def get_employee_by_telegram_id_or_username(self, telegram_id: str | None = None,
                                                      telegram_username: str | None = None):
        async  with db.Session() as request:
            if telegram_id is None and telegram_username is None:
                raise TelegramIdOrUsernameError("Необходимо задать telegram_id или telegram_username")

            # Выполняем запрос с использованием фильтра
            if telegram_id:
                query = select(Employees).filter_by(telegram_id=telegram_id)  # Поиск по telegram_id
            else:
                query = select(Employees).filter_by(telegram_username=telegram_username)  # Поиск по telegram_username

            result = await request.execute(query)

            return result.scalar_one_or_none()
