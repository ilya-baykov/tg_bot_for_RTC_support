import asyncio
import logging
import platform

from database.CRUD.сreate import ActionsCreator
from main_objects import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Установите политику цикла событий для Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def preparation_for_launch():
    # await db.reset_database()  # Очищает БД
    # await db.create_db()  # Создает все модели в БД
    await ActionsCreator().create_new_action()  # Считываем входную таблицу и формируем актуальные задачи
    # Вызывать бота


if __name__ == '__main__':
    asyncio.run(preparation_for_launch())
