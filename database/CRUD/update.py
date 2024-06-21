import datetime
import logging

from main_objects import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmployeesUpdater:

    @staticmethod
    async def update_status(employee, status):
        """Изменяет статус сотрудника"""
        async with db.Session() as request:
            # Получаем сотрудника
            employee = await request.merge(employee)

            # Вносим изменения в статус
            employee.status = status
            logger.info(f"Сотрудник №{employee.id} изменение в статусе :{status}")

            # Сохраняем изменения
            await request.commit()


class ActionsUpdater:
    @staticmethod
    async def update_status(action, status):
        """Изменяет статус действия"""
        async with db.Session() as request:
            # Получаем действие
            action = await request.merge(action)

            # Вносим изменения в статус
            action.status = status
            logger.info(f"Действие №{action.id} изменение в статусе :{status}")
            # Сохраняем изменения
            await request.commit()

    @staticmethod
    async def update_actual_time_message(action, time: datetime.datetime):
        """Устанавливает или изменяет время запуска задачи (отправки сообщения)"""
        async with db.Session() as request:
            action = await action.merge(action)
            action.actual_time_message = time
            logger.info(f"Для задачи №{action.id} установлено время запуск: {time}")
            await request.commit()
