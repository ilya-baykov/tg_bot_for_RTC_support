import logging

from main_objects import db
from database.models import *
from database.CRUD.read import EmployeesReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

employees_reader = EmployeesReader()


class EmployeesCreator:
    async def create_new_employees(self, name: str | None, telegram_username: str, telegram_id: str | int):
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
