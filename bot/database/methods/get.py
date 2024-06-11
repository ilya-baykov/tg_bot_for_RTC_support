import datetime

from sqlalchemy import select

from bot.database.database_main import session_factory
from bot.database.models.main_models import TaskEntry


def select_future_tasks():
    with session_factory() as session:
        query = select(TaskEntry).filter(TaskEntry.scheduled_time > datetime.datetime.now())
        result = session.execute(query)
        future_tasks = result.scalars().all()
        print(future_tasks)


select_future_tasks()
