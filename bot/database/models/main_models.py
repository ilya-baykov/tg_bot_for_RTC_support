import datetime

from sqlalchemy import ForeignKey, func, Interval, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column
#
# from bot.database.database_main import Base, str_100, str_50
# from bot.database.models.type_annotation_map import intpk, text, DateTimeNotNull, Status

from bot.database.database_main import Base


def register_models() -> None:
    pass


# Модели таблиц

class TaskEntry(Base):
    __tablename__ = 'task_entries'

    entry_id: Mapped[int] = mapped_column(primary_key=True)  # уникальный идентификатор записи
    process_name: Mapped[str]  # имя процесса
    action_description: Mapped[str]  # описание действия
    employee_telegram: Mapped[str]  # телеграм сотрудника
    scheduled_time: Mapped[datetime.datetime]  # время, когда нужно отправить сообщение сотруднику


class Employee(Base):
    __tablename__ = 'employees'

    employee_id: Mapped[int] = mapped_column(primary_key=True)  # уникальный идентификатор сотрудника
    telegram_id: Mapped[str]  # идентификатор телеграмма сотрудника
    name: Mapped[str] = mapped_column(nullable=True)  # имя сотрудника


class Process(Base):
    __tablename__ = 'processes'

    process_id: Mapped[int] = mapped_column(primary_key=True)  # уникальный идентификатор процесса
    process_name: Mapped[str]  # имя процесса
    action_description: Mapped[str]  # описание действия

    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.employee_id'),
                                             nullable=False)  # идентификатор сотрудника, ответственного за процесc

    scheduled_time: Mapped[datetime.datetime]  # время, когда нужно отправить сообщение сотруднику

    employee = relationship('Employee')


class Notification(Base):
    __tablename__ = 'notifications'

    notification_id: Mapped[int] = mapped_column(primary_key=True)  # уникальный идентификатор уведомления

    process_id: Mapped[int] = mapped_column(ForeignKey('processes.process_id'),
                                            nullable=False)  # идентификатор процесса

    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.employee_id'),
                                             nullable=False)  # идентификатор сотрудника, получившего уведомление

    sent_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())  # время отправки уведомления
    response_time: Mapped[datetime.datetime]  # время ответа
    response_status: Mapped[str]  # статус ответа
    comment: Mapped[str] = mapped_column(nullable=True)  # комментарий сотрудника
    response_duration: Mapped[Interval] = mapped_column(Interval, nullable=True)  # время, потраченное на ответ

    process = relationship('Process')
    employee = relationship('Employee')
