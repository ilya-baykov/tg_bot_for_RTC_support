from bot.database.database_main import Base, session_factory, engine
from bot.database.models.main_models import TaskEntry, Employee, Process, Notification


def create_tables():
    engine.echo = True
    Base.metadata.create_all(engine)


# create_tables()
