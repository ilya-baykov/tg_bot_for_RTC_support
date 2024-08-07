import asyncio
import platform
from main_objects import db
from run_app.bot_running import start_bot
from utility.sheduler_functions import start_scheduler
from utility.updating_daily_tasks import updating_daily_tasks


async def preparation_for_launch():
    # await db.reset_database()  # Очищает БД
    await db.create_db()  # Создает все модели в БД

    await start_scheduler()  # Запуск планировщика заданий
    await updating_daily_tasks()  # Формирование актуальных задач

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
