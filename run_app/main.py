import asyncio
import logging
import platform

from main_objects import start_scheduler, scheduler
from run_app.bot_running import start_bot
from database.CRUD.read import ActionsReader, EmployeesReader
from database.CRUD.сreate import ActionsCreator
from sent_task_to_emploeyee.sending_messages import add_task_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Установите политику цикла событий для Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def preparation_for_launch():
    await start_scheduler(scheduler)

    # await db.reset_database()  # Очищает БД
    # await db.create_db()  # Создает все модели в БД
    await ActionsCreator().create_new_action()  # Считываем входную таблицу и формируем актуальные задачи

    pending_actions = await ActionsReader().get_pending_actions()  # Получаем все задачи, ожидающие отправки

    for action in pending_actions:
        await add_task_scheduler(scheduler=scheduler, action_task=action)  # Передаем задачи в планировщик

    await start_bot()


if __name__ == '__main__':
    asyncio.run(preparation_for_launch())
