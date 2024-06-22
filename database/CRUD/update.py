import datetime
import logging
from database.models import Actions

from run_app.main_objects import db

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
            # Получаем объект действия из базы данных
            action_obj = await request.get(Actions, action.id)

            if action_obj:
                # Обновляем статус действия
                action_obj.status = status
                logger.info(f"Действие №{action_obj.id} изменение в статусе: {status}")

                # Сохраняем изменения
                await request.commit()
            else:
                logger.warning(f"Действие с ID {action.id} не найдено в базе данных.")

    @staticmethod
    async def update_actual_time_message(action, time: datetime.datetime):
        """Устанавливает или изменяет время запуска задачи (отправки сообщения)"""
        async with db.Session() as request:
            action_obj = await request.get(Actions, action.id)

            if action_obj:
                # Обновляем время запуска у действия
                action_obj.actual_time_message = time

                logger.info(f"Для задачи №{action.id} установлено время запуск: {time}")

                # Сохраняем изменения
                await request.commit()
            else:
                logger.warning(f"Действие с ID {action.id} не найдено в базе данных.")
