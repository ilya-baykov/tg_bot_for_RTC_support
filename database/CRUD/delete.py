import logging

from sqlalchemy import delete

from database.models import ActionsToday, SchedulerTasks, ClearInputData
from run_app.main_objects import db

logger = logging.getLogger(__name__)


class ActionsTodayDeleter:
    @staticmethod
    async def clear_table():
        """Очищаем таблицу ActionsToday"""
        async with db.Session() as request:
            logger.info("Очистка таблицы actions_today...")
            await request.execute(delete(ActionsToday))
            await request.commit()
            logger.info("Таблица actions_today была успешно очищена")


class SchedulerTasksDeleter:
    @staticmethod
    async def clear_table():
        """Очищает таблицу scheduler_tasks"""
        async with db.Session() as request:
            logger.info("Очистка таблицы scheduler_tasks...")
            await request.execute(delete(SchedulerTasks))
            await request.commit()
            logger.info("Таблица scheduler_tasks была успешно очищена")


class ClearInputDataDeleter:
    @staticmethod
    async def clear_table():
        """Очищаем таблицу clear_input_data"""
        async with db.Session() as request:
            logger.info("Очистка таблицы clear_input_data...")
            await request.execute(delete(ClearInputData))
            await request.commit()
            logger.info("Таблица clear_input_data была успешно очищена")
