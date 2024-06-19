import datetime
import enum
from typing import Annotated
from sqlalchemy import ForeignKey, func, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column
from database.Base import Base, str_20, str_50, str_100, str_512

intpk = Annotated[int, mapped_column(primary_key=True)]


class ProcessStatus(enum.Enum):
    queued_to_be_added = "В очереди на добавление"
    waiting_to_be_sent = "Ожидает отправки"
    sent = "Отправлено"
    completed = "Выполнено"


class NotificationProcessStatus(enum.Enum):
    ok = "ОК"
    not_ok = "НЕ ОК"


class EmployeeStatus(enum.Enum):
    available = "Свободен"
    busy = "Занят"


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
    telegram_username: Mapped[str_50]  # username телеграмма сотрудника
    telegram_id: Mapped[str_50]  # идентификатор телеграмма сотрудника
    name: Mapped[str_50] = mapped_column(nullable=True)  # имя сотрудника
    status: Mapped[EmployeeStatus] = mapped_column(default=EmployeeStatus.available)


class EmployeePhones(Base):
    __tablename__ = 'employee_phones'

    employee_phones_id: Mapped[intpk]  # Уникальный идентификатор

    fullname: Mapped[str_100]
    phone_number: Mapped[str_20] = mapped_column(nullable=True)


class Process(Base):
    __tablename__ = 'processes'

    process_id: Mapped[intpk]  # уникальный идентификатор процесса
    process_name: Mapped[str_100]  # имя процесса
    action_description: Mapped[str_512]  # описание действия

    status: Mapped[ProcessStatus] = mapped_column(default=ProcessStatus.queued_to_be_added)

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
    response_status: Mapped[NotificationProcessStatus]  # статус ответа
    comment: Mapped[str_512] = mapped_column(nullable=True)  # комментарий сотрудника
    response_duration: Mapped[datetime.datetime]  # время, потраченное на ответ

    process = relationship('Process')
    employee = relationship('Employee')
