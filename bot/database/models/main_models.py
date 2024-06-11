import datetime
import enum
from typing import Annotated
from sqlalchemy import ForeignKey, func, Interval, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column
from bot.database.database_main import Base, str_50, str_100, str_512


def register_models() -> None:
    pass


intpk = Annotated[int, mapped_column(primary_key=True)]


class Status(enum.Enum):
    ok = "ОК"
    not_ok = "НЕ ОК"


# Модели таблиц

class TaskEntry(Base):
    __tablename__ = 'task_entries'

    entry_id: Mapped[intpk]  # уникальный идентификатор записи
    process_name: Mapped[str_100]  # имя процесса
    action_description: Mapped[str_512]  # описание действия
    employee_telegram: Mapped[str_50]  # телеграм сотрудника

    scheduled_time: Mapped[datetime.datetime]  # время, когда нужно отправить сообщение сотруднику


class Employee(Base):
    __tablename__ = 'employees'

    employee_id: Mapped[intpk]  # уникальный идентификатор сотрудника
    telegram_id: Mapped[str_50]  # идентификатор телеграмма сотрудника
    name: Mapped[str_50] = mapped_column(nullable=True)  # имя сотрудника

class Process(Base):
    __tablename__ = 'processes'

    process_id: Mapped[intpk]  # уникальный идентификатор процесса
    process_name: Mapped[str_100]  # имя процесса
    action_description: Mapped[str_512]  # описание действия

    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.employee_id'),
                                             nullable=False)  # идентификатор сотрудника, ответственного за процесc

    scheduled_time: Mapped[datetime.datetime]  # время, когда нужно отправить сообщение сотруднику

    employee = relationship('Employee')


class Notification(Base):
    __tablename__ = 'notifications'

    notification_id: Mapped[intpk]  # уникальный идентификатор уведомления

    process_id: Mapped[int] = mapped_column(ForeignKey('processes.process_id'))  # идентификатор процесса

    employee_id: Mapped[int] = mapped_column(
        ForeignKey('employees.employee_id'))  # идентификатор сотрудника, получившего уведомление

    sent_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())  # время отправки уведомления
    response_time: Mapped[datetime.datetime]  # время ответа
    response_status: Mapped[Status]  # статус ответа
    comment: Mapped[str_512] = mapped_column(nullable=True)  # комментарий сотрудника
    response_duration: Mapped[datetime.datetime]  # время, потраченное на ответ

    process = relationship('Process')
    employee = relationship('Employee')
