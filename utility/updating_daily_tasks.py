import datetime
from os import environ

from database.CRUD.delete import ActionsTodayDeleter, SchedulerTasksDeleter, ClearInputDataDeleter
from database.CRUD.read import ActionsTodayReader
from database.CRUD.сreate import ActionsTodayCreator, ClearInputDataCreator
from logger_settings.setup_logger import setup_logger
from run_app.main_objects import load_json
from sent_task_to_emploeyee.sending_messages import add_task_scheduler


async def updating_daily_tasks():
    """Функция, которая будет запускаться каждый день для формирования актуальных задач"""
    logger = setup_logger()  # Загрузка настроек логирования
    logger.info("Запуск функции updating_daily_tasks ")
    await ActionsTodayDeleter().clear_table()
    await SchedulerTasksDeleter().clear_table()
    await ClearInputDataDeleter().clear_table()

    # Проверка рабочего дня
    if str(datetime.date.today()) not in (await load_json(path=environ.get('JSON_PATH', 'define me!')))['dates']:

        await ClearInputDataCreator().create_clear_data()  # Формирует данные в таблице ClearInputData
        await ActionsTodayCreator().create_new_actions()  # Считываем ClearInputData и формируем актуальные задачи

        pending_actions = await ActionsTodayReader().get_pending_actions()  # Получаем все задачи, ожидающие отправки
        for action in pending_actions:
            await add_task_scheduler(action_task=action)  # Передаем задачи в планировщик
        logger.info(f"Ежедневные задачи обновлены в {datetime.datetime.now()}")

    else:
        logger.info(f"Сегодня нерабочий день, задачи не обновлены в {datetime.datetime.now()}")
