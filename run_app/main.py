import asyncio
import datetime
import logging
import platform

from database.CRUD.delete import ActionsTodayDeleter, SchedulerTasksDeleter
from main_objects import start_scheduler, scheduler, db
from run_app.bot_running import start_bot
from database.CRUD.read import ActionsTodayReader
from database.CRUD.сreate import ActionsTodayCreator
from sent_task_to_emploeyee.sending_messages import add_task_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def updating_daily_tasks():
    """Функция, которая будет запускаться каждый день для формирования актуальных задач"""
    await ActionsTodayDeleter().clear_table()
    await SchedulerTasksDeleter().clear_table()

    await ActionsTodayCreator().create_new_actions()  # Считываем входную таблицу и формируем актуальные задачи
    logger.info(f"Ежедненвые задачи обновлены в {datetime.datetime.now()}")

    pending_actions = await ActionsTodayReader().get_pending_actions()  # Получаем все задачи, ожидающие отправки

    for action in pending_actions:
        await add_task_scheduler(scheduler=scheduler, action_task=action)  # Передаем задачи в планировщик


async def preparation_for_launch():
    # await db.reset_database()  # Очищает БД
    # await db.create_db()  # Создает все модели в БД

    await start_scheduler(scheduler)  # Запуск планировщика заданий
    await updating_daily_tasks()  # Формирование актуальных задач

    # Добавляем задачу, которая будет выполняться каждый день в 00:00:00
    scheduler.add_job(updating_daily_tasks, trigger="cron", hour=0, minute=0, second=0)

    await start_bot()


if __name__ == '__main__':

    try:
        # Установите политику цикла событий для Windows
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        asyncio.run(preparation_for_launch())
    except Exception as e:
        print(e)
