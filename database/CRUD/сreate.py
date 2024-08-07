import logging
from datetime import timedelta, datetime
from database.CRUD.update import EmployeesUpdater, UserAccessUpdater
from run_app.main_objects import db
from database.models import *
from database.CRUD.read import EmployeesReader, ClearInputTableReader, ActionsTodayReader, UserAccessReader, \
    SchedulerTasksReader, RawInputTable
from utility.ActionDecisionToday import ActionDecisionToday

logger = logging.getLogger(__name__)

employees_reader = EmployeesReader()
clear_input_table_reader = ClearInputTableReader()
employees_updater = EmployeesUpdater()
actions_today_reader = ActionsTodayReader()


class EmployeesCreator:
    @staticmethod
    async def create_new_employees(name: str | None, telegram_username: str, telegram_id: str | int):
        """Добавляем / Регистрируем нового сотрудника или изменяем username у текущего сотрудника """
        async with db.Session() as request:
            employee = await employees_reader.get_employee_by_telegram_id_or_username(telegram_id=str(telegram_id))
            if employee:
                # Если сотрудник изменил username - заменяем значение в таблице
                if employee.telegram_username != telegram_username:
                    employee.telegram_username = telegram_username
                    await request.commit()
                    logger.info(f"Telegram username для telegram_id '{telegram_id}' обновлен на '{telegram_username}'.")

            else:
                # Создать нового сотрудника
                request.add(Employees(
                    name=name,
                    telegram_username=telegram_username,
                    telegram_id=telegram_id,
                ))
                logger.info(f"Пользователь с telegram_id '{telegram_id}' добавлен в таблицу employees.")

                await request.commit()


class ActionsTodayCreator:

    @staticmethod
    async def create_new_actions():
        """Формируем актуальные задачи из исходной таблицы """
        async with db.Session() as session:
            tasks = await clear_input_table_reader.get_all_actions()  # Получаем список всех задач из входной таблицы
            busy_employees = {}  # Словарь 'занятых' сотрудников

            for task in tasks:
                if ActionDecisionToday(interval=task.interval, day_of_action=task.completion_day).make_decision():
                    logger.info(f"Задача с ID:{task.id} будет добавлена в список действий на текущий день")
                    await ActionsTodayCreator.process_task(task, busy_employees, session)
                else:
                    logger.info(f"Задача с ID:{task.id} не будет добавлена в список действий на текущий день")

    @staticmethod
    async def create_action(task, employee, status, session):
        """Создание новой задачи"""
        session.add(ActionsToday(
            input_data_id=task.id,
            employee_id=employee.id,
            status=status
        ))
        await session.commit()
        logger.info(f"Задача {task.process_name} была добавлена со статусом {status}")

    @staticmethod
    async def process_task(task, busy_employees, session):
        """Обрабатываем задачу"""
        if await ActionsTodayCreator.is_task_already_created(task):
            logger.info(f"Задача {task.id} уже была создана.")
            return

        employee, status = await ActionsTodayCreator.assign_employee_and_status(task, busy_employees)
        if not employee:
            logger.warning(f"Сотрудник с telegram_username '{task.telegram_username}' не найден.")
            return

        await ActionsTodayCreator.create_action(task, employee, status, session)

    @staticmethod
    async def is_task_already_created(task):
        """Проверка наличия задачи в таблице actions"""
        return await actions_today_reader.get_action(task.id) is not None

    @staticmethod
    async def assign_employee_and_status(task, busy_employees):
        """Назначение сотрудника и статуса задачи"""
        if task.telegram_username in busy_employees:
            employee = busy_employees[task.telegram_username]
            status = ActionStatus.queued_to_be_added
        else:
            employee = await employees_reader.get_employee_by_telegram_id_or_username(
                telegram_username=task.telegram_username)
            if not employee:
                return None, None

            busy_employees[task.telegram_username] = employee
            status = await ActionsTodayCreator.determine_status(employee)

        return employee, status

    @staticmethod
    async def determine_status(employee):
        """Определение статуса задачи на основе количества задач у сотрудника"""
        tasks_count = await employees_reader.get_all_employee_tasks(employee.id)
        return ActionStatus.queued_to_be_added if len(tasks_count) > 0 else ActionStatus.waiting_to_be_sent


class ReportCreator:
    @staticmethod
    async def create_new_report(process_name: str, action_description: str, employee_name: str,
                                expected_dispatch_time: datetime,
                                actual_dispatch_time: datetime, employee_response_time: datetime,
                                elapsed_time: timedelta, status: FinalStatus, comment: str):
        async with db.Session() as request:
            request.add(Report(
                process_name=process_name,
                action_description=action_description,
                employee_name=employee_name,
                expected_dispatch_time=expected_dispatch_time,
                actual_dispatch_time=actual_dispatch_time,
                employee_response_time=employee_response_time,
                elapsed_time=elapsed_time,
                status=status.value,
                comment=comment
            ))
            await request.commit()
            logger.info(f"Добавлена запись в отчетную таблицу. № Действия {process_name} со статусом {status}")


class UserAccessCreator:
    @staticmethod
    async def create_new_user(telegram_id: str):
        """Создает информацию о пользователь в таблице user_access"""
        async with db.Session() as request:
            user = await UserAccessReader.get_user(telegram_id=telegram_id)
            if user:
                await UserAccessUpdater.update_number_of_attempts(user)
            else:
                request.add(UserAccess(
                    telegram_id=telegram_id,
                    number_of_attempts=1

                ))
                await request.commit()
                logger.info(f"Добавлена запись о пользователе с telegram_id = {telegram_id}")


class SchedulerTasksCreator:
    @staticmethod
    async def create_new_task(scheduler_task_id: str, employee_id: int,
                              expected_completion_time: datetime.datetime) -> None:
        async with db.Session() as request:
            scheduler_task = await SchedulerTasksReader.get_tasks(scheduler_task_id)
            if scheduler_task:
                logger.warning(f"В планировщике заданий уже есть действие с id {scheduler_task_id}")
            else:
                request.add(SchedulerTasks(
                    id=scheduler_task_id,
                    employee_id=employee_id,
                    expected_completion_time=expected_completion_time
                ))
                await request.commit()


class ClearInputDataCreator:
    @staticmethod
    async def create_clear_data():
        """Формирует данные в таблице ClearInputData """
        async with db.Session() as request:
            raw_data = await RawInputTable.get_row_table_data()
            for row in raw_data:
                scheduled_time: list = row.scheduled_time.split(',')  # Список времён для запуска процесса
                for time_str in scheduled_time:
                    try:
                        time = datetime.datetime.strptime(time_str.strip(), "%H:%M").time()
                    except ValueError:
                        continue
                    request.add(ClearInputData(
                        process_name=row.process_name,
                        action_description=row.action_description,
                        telegram_username=row.telegram_username,
                        interval=row.interval,
                        completion_day=row.completion_day,
                        scheduled_time=time,
                        priority=row.priority

                    ))
                    logger.info(f"В таблицу clear_input_table была добавлена запись {row.process_name}:{time}")
            await request.commit()


class OperationLogCreator:
    @staticmethod
    async def create_new_log(process_name: str, employee_name: str, error_description: str, error_date: str | None,
                             error_reason: str | None, error_solution: str | None,
                             error_type: str | None, developer: str | None, jira_link: str | None,
                             decision_date: str | None, jira_issue: str | None, virtual_machine: str,
                             execution_time: str | None, OTRS_ticket: str | None):
        async with db.Session() as request:
            request.add(OperationLog(
                process_name=process_name,  # Номер RPA
                employee_name=employee_name,  # Имя сотрудника, отвечающего за процесс
                error_description=error_description,  # Описание ошибки
                error_date=error_date,  # Дата ошибки в произвольной форме
                error_reason=error_reason,  # Причина ошибки
                error_solution=error_solution,  # Решение ошибки
                error_type=error_type,  # Один из вариантов типа ошибок
                developer=developer,  # Разработчик, отвечающий за процесс
                jira_link=jira_link,  # Ссылка на робота в Jira
                decision_date=decision_date,  # Дата устранения ошибки в произвольной форме
                OTRS_ticket=OTRS_ticket,  # Ссылка на тикет в OTRS
                jira_issue=jira_issue,  # Ссылка на задачу в Jira
                virtual_machine=virtual_machine,  # Номер виртуальной машины
                execution_time=execution_time  # Время выполнения в ч.
            ))
            await request.commit()
            logger.info(f"Добавлена запись в журнал эксплуатации. Имя процесса - {process_name}")
