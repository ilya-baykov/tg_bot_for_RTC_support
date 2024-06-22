import asyncio
import logging
import platform

from main_objects import start_scheduler, scheduler, db
from run_app.bot_running import start_bot
from database.CRUD.read import ActionsTodayReader, EmployeesReader
from database.CRUD.сreate import ActionsTodayCreator
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
    await ActionsTodayCreator().create_new_actions()  # Считываем входную таблицу и формируем актуальные задачи

    pending_actions = await ActionsTodayReader().get_pending_actions()  # Получаем все задачи, ожидающие отправки

    for action in pending_actions:
        await add_task_scheduler(scheduler=scheduler, action_task=action)  # Передаем задачи в планировщик

    await start_bot()


if __name__ == '__main__':
    asyncio.run(preparation_for_launch())
