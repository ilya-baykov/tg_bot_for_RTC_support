import datetime
from typing import Annotated
from sqlalchemy import ForeignKey, Interval
from sqlalchemy.orm import Mapped, relationship, mapped_column
from database_old.Base import Base, str_20, str_50, str_100, str_512
from database.enums import *

intpk = Annotated[int, mapped_column(primary_key=True)]


class InputData(Base):
    __tablename__ = "input_table"

    id: Mapped[intpk]
    process_name: Mapped[str_100]
    action_description: Mapped[str_512]
    telegram_username: Mapped[str_50]
    interval: Mapped[IntervalType]  # Возможные варианты запуска (Каждый день, раз в месяц, разовое выполнение)

    completion_day: Mapped[str_50] = mapped_column(nullable=True)  # День когда запускать процесс
    scheduled_time: Mapped[datetime.datetime]  # Время отправки сообщения об процессе


class Actions(Base):
    __tablename__ = "actions"

    id: Mapped[intpk]
    input_data_id: Mapped[int | None] = mapped_column(
        ForeignKey('input_table.id', ondelete="SET NULL"))  # Ссылка на действие из входной таблицы

    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'))  # Ссылка на сотрудника из таблицы сотрудников
    status: Mapped[ActionStatus]  # Одно из возможных состояний процесса
    actual_time_message: Mapped[datetime.datetime] = mapped_column(nullable=True)

    input_table = relationship("InputData")
    employee = relationship("Employees")


class Employees(Base):
    __tablename__ = 'employees'

    id: Mapped[intpk]
    telegram_username: Mapped[str_50]  # username в телеграмме сотрудника
    telegram_id: Mapped[str_50]  # идентификатор телеграмма сотрудника
    status: Mapped[EmployeesStatus]


class EmployeesContact(Base):
    __tablename__ = "employees_contact"

    id: Mapped[intpk]
    phone_number: Mapped[str_20]
    fullname: Mapped[str_100]


class Report(Base):
    __tablename__ = "report_table"

    id: Mapped[intpk]
    action_id: Mapped[int | None] = mapped_column(
        ForeignKey('actions.id', ondelete="SET NULL"))  # Ссылка на действие из таблицы действий
    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey('employees.id', ondelete="SET NULL"))  # Ссылка на сотрудника из таблицы сотрудников

    expected_dispatch_time: Mapped[datetime.datetime]
    actual_dispatch_time: Mapped[datetime.datetime]
    employee_response_time: Mapped[datetime.datetime]
    elapsed_time: Mapped[datetime.timedelta] = mapped_column(Interval)

    status: Mapped[FinalStatus]
    comment: Mapped[str_512]

    actions = relationship("Actions")
    employee = relationship("Employees")
