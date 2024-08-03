import asyncio
import datetime
import platform
from os import environ

from database.CRUD.delete import ActionsTodayDeleter, SchedulerTasksDeleter, ClearInputDataDeleter
from logger_settings.setup_logger import setup_logger
from main_objects import scheduler, load_json, db
from run_app.bot_running import start_bot
from database.CRUD.read import ActionsTodayReader
from database.CRUD.сreate import ActionsTodayCreator, ClearInputDataCreator
from sent_task_to_emploeyee.sending_messages import add_task_scheduler
from utility.sheduler_functions import start_scheduler


async def updating_daily_tasks():
    """Функция, которая будет запускаться каждый день для формирования актуальных задач"""
    logger = setup_logger()  # Загрузка настроек логирования

    await ActionsTodayDeleter().clear_table()
    await SchedulerTasksDeleter().clear_table()
    await ClearInputDataDeleter().clear_table()

    # Проверка рабочего дня
    if str(datetime.date.today()) not in (await load_json(path=environ.get('JSON_PATH', 'define me!')))['dates'] or True:

        await ClearInputDataCreator().create_clear_data()  # Формирует данные в таблице ClearInputData
        await ActionsTodayCreator().create_new_actions()  # Считываем ClearInputData и формируем актуальные задачи

        pending_actions = await ActionsTodayReader().get_pending_actions()  # Получаем все задачи, ожидающие отправки
        for action in pending_actions:
            await add_task_scheduler(action_task=action)  # Передаем задачи в планировщик
        logger.info(f"Ежедневные задачи обновлены в {datetime.datetime.now()}")

    else:
        logger.info(f"Сегодня нерабочий день, задачи не обновлены в {datetime.datetime.now()}")


async def preparation_for_launch():
    # await db.reset_database()  # Очищает БД
    # await db.create_db()  # Создает все модели в БД

    await start_scheduler()  # Запуск планировщика заданий
    await updating_daily_tasks()  # Формирование актуальных задач

    # Добавляем задачу, которая будет выполняться каждый день в 00:00:00
    scheduler.add_job(updating_daily_tasks, trigger="cron", hour=0, minute=0, second=0, misfire_grace_time=60)

    await start_bot()


if __name__ == '__main__':
    print("Бот запущен")
    try:
        # Установите политику цикла событий для Windows
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        asyncio.run(preparation_for_launch())
    except Exception as e:
        print(e)
