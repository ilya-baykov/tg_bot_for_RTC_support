import logging
from datetime import timedelta, datetime

from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.date import DateTrigger

from database.CRUD.read import SchedulerTasksReader
from database.CRUD.update import SchedulerTasksUpdater
from database.enums import SchedulerStatus
from database.models import SchedulerTasks
from run_app.main_objects import scheduler

logger = logging.getLogger(__name__)


async def start_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)  # Закрываем прошлый планировщик задач
        logger.info("Прошлые задачи планировщика были очищены")

    scheduler.start()
    logger.info(f"Планировщик заданий {scheduler} запущен")
    logger.info("Все предыдущие задачи планировщика были удалены")


async def pause_scheduler_task(task_in_scheduler: SchedulerTasks) -> None:
    """Ставит конкретную задачу из планировщика на паузу
    """
    if task_in_scheduler:
        try:
            scheduler.pause_job(task_in_scheduler.id)
            # Изменяем статус задачи в планировщике
            await SchedulerTasksUpdater.update_params(task=task_in_scheduler, status=SchedulerStatus.suspended)
            logger.info(f"Задача с ID {task_in_scheduler.id} остановлена.")
        except JobLookupError:
            logger.error(f"Задача с ID {task_in_scheduler.id} не найдена в планировщике.")
        except Exception as e:
            print(e)


async def resume_scheduler_task(task_in_scheduler_id: SchedulerTasks.id) -> None:
    """Возобновляет задачу в планировщике заданий"""
    current_time = datetime.now()
    task_in_scheduler = await SchedulerTasksReader.get_tasks(task_in_scheduler_id)

    # Если следующая задача должна была выполниться - переводим время
    if task_in_scheduler.expected_completion_time > current_time + timedelta(seconds=10):
        time = task_in_scheduler.expected_completion_time
    else:
        time = current_time + timedelta(seconds=10)

    await SchedulerTasksUpdater.update_params(task=task_in_scheduler,
                                              status=SchedulerStatus.awaiting_dispatch,
                                              time=time)

    new_trigger = DateTrigger(run_date=time)

    # Изменение времени задачи
    scheduler.modify_job(task_in_scheduler_id, trigger=new_trigger)
    # Возобновление задачи
    scheduler.resume_job(task_in_scheduler_id)

    logger.info(f"Время выполнения задачи с ID {task_in_scheduler_id} установлено на :{time}.")
