import logging

from sqlalchemy import delete

from database.models import ActionsToday
from run_app.main_objects import db

logging.basicConfig(level=logging.INFO)
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
