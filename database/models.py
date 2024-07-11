import datetime
from typing import Annotated
from sqlalchemy import ForeignKey, Interval, Time, Enum as PgEnum
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database.Base import Base, str_20, str_50, str_100, str_512
from database.enums import *

intpk = Annotated[int, mapped_column(primary_key=True)]


class RawInputData(Base):
    __tablename__ = "raw_input_table"

    id: Mapped[intpk]
    process_name: Mapped[str_100]  # Имя процесса
    action_description: Mapped[str_512]  # Описание действия
    telegram_username: Mapped[str_50]  # Имя пользователя в телеграмме сотрудника
    interval: Mapped[IntervalType]  # Возможные варианты запуска (Каждый день, раз в месяц, разовое выполнение)

    completion_day: Mapped[str_50] = mapped_column(nullable=True)  # День когда запускать процесс
    scheduled_time: Mapped[str_50] = mapped_column(nullable=True)  # Время отправки сообщения об процессе


class ClearInputData(Base):
    __tablename__ = "clear_input_table"

    id: Mapped[intpk]
    process_name: Mapped[str_100]
    action_description: Mapped[str_512]
    telegram_username: Mapped[str_50]
    interval: Mapped[IntervalType]  # Возможные варианты запуска (Каждый день, раз в месяц, разовое выполнение)

    completion_day: Mapped[str_50] = mapped_column(nullable=True)  # День когда запускать процесс
    scheduled_time: Mapped[datetime.time] = mapped_column(Time)  # Время отправки сообщения об процессе


class ActionsToday(Base):
    __tablename__ = "actions_today"

    id: Mapped[intpk]
    input_data_id: Mapped[int | None] = mapped_column(
        ForeignKey('clear_input_table.id', ondelete="SET NULL"))  # Ссылка на действие из входной таблицы

    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'))  # Ссылка на сотрудника из таблицы сотрудников

    status: Mapped[ActionStatus] = mapped_column(default=ActionStatus.queued_to_be_added)

    actual_time_message: Mapped[datetime.datetime] = mapped_column(nullable=True)

    clear_input_table = relationship("ClearInputData")
    employee = relationship("Employees")


class Employees(Base):
    __tablename__ = 'employees'

    id: Mapped[intpk]
    name: Mapped[str_50] = mapped_column(nullable=True)
    telegram_username: Mapped[str_50]  # username в телеграмме сотрудника
    telegram_id: Mapped[str_50]  # идентификатор телеграмма сотрудника
    status: Mapped[EmployeesStatus] = mapped_column(default=EmployeesStatus.available)


class SchedulerTasks(Base):
    __tablename__ = 'scheduler_tasks'

    id: Mapped[str_50] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'))  # Ссылка на сотрудника из таблицы сотрудников
    status: Mapped[SchedulerStatus] = mapped_column(default=SchedulerStatus.awaiting_dispatch)

    expected_completion_time: Mapped[datetime.datetime] = mapped_column(
        nullable=True)  # Ожидаемое время выполнения задачи

    employee = relationship("Employees")


class EmployeesContact(Base):
    __tablename__ = "employees_contact"

    id: Mapped[intpk]
    phone_number: Mapped[str_20]
    fullname: Mapped[str_100]


class Report(Base):
    __tablename__ = "report_table"

    id: Mapped[intpk]
    process_name: Mapped[str_100]  # Имя выполненного процесса
    action_description: Mapped[str_512]  # Описание выполненного действия
    employee_name: Mapped[str_50] = mapped_column(nullable=True)  # Имя сотрудника, отвечающего за процесс
    expected_dispatch_time: Mapped[datetime.datetime]  # Ожидаемое время отправки сообщения сотруднику
    actual_dispatch_time: Mapped[datetime.datetime]  # Фактическое время отправки сообщения сотруднику
    employee_response_time: Mapped[datetime.datetime]  # Фиксация времени ответа сотрудником
    elapsed_time: Mapped[datetime.timedelta] = mapped_column(Interval)  # Разница времени (время на ответ)

    status: Mapped[str_50]


    comment: Mapped[str_512]


class UserAccess(Base):
    __tablename__ = "user_access"
    id: Mapped[intpk]
    telegram_id: Mapped[str_50]  # идентификатор телеграмма сотрудника
    user_status: Mapped[UserStatus] = mapped_column(default=UserStatus.available)  # Статус пользователя
    number_of_attempts: Mapped[int] = mapped_column(default=0)  # Количество попыток авторизации
