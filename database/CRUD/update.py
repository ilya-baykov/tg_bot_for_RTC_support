import datetime
import logging

from database.enums import UserStatus, SchedulerStatus, FinalStatus
from database.models import ActionsToday, UserAccess, SchedulerTasks, Report

from run_app.main_objects import db

logger = logging.getLogger(__name__)


class EmployeesUpdater:

    @staticmethod
    async def update_status(employee, status):
        """Изменяет статус сотрудника"""
        async with db.Session() as request:
            # Получаем сотрудника
            employee = await request.merge(employee)

            # Вносим изменения в статус
            employee.status = status
            logger.info(f"Сотрудник №{employee.id} изменение в статусе :{status}")

            # Сохраняем изменения
            await request.commit()


class ActionsTodayUpdater:
    @staticmethod
    async def update_status(action, status):
        """Изменяет статус действия"""
        async with db.Session() as request:
            # Получаем объект действия из базы данных
            action_obj = await request.get(ActionsToday, action.id)

            if action_obj:
                # Обновляем статус действия
                action_obj.status = status
                logger.info(f"Действие №{action_obj.id} изменение в статусе: {status}")

                # Сохраняем изменения
                await request.commit()
            else:
                logger.warning(f"Действие с ID {action.id} не найдено в базе данных.")

    @staticmethod
    async def update_actual_time_message(action: ActionsToday, time: datetime.time | None = None):
        """Устанавливает или изменяет время запуска задачи (отправки сообщения)"""
        async with db.Session() as request:
            action_obj = await request.get(ActionsToday, action.id)

            if action_obj:
                if time is None:
                    time = datetime.datetime.now().time()  # Устанавливаем текущее время по умолчанию

                # Обновляем время запуска у действия
                action_obj.actual_time_message = datetime.datetime.combine(datetime.datetime.today(), time)

                logger.info(f"Для задачи №{action.id} установлено время запуск: {time}")

                # Сохраняем изменения
                await request.commit()
            else:
                logger.warning(f"Действие с ID {action.id} не найдено в базе данных.")


class UserAccessUpdater:
    @staticmethod
    async def update_user_status(user: UserAccess) -> None:
        """Обновляет статус пользователя если привышено количество попыток авторизации"""
        async with db.Session() as request:
            # Получаем пользователя из таблицы user_access
            user_obj = await request.get(UserAccess, user.id)

            if user_obj:
                # Проверяем количество попыток авторизации
                if user_obj.number_of_attempts > 3:
                    # Обновляем статус действия
                    user_obj.user_status = UserStatus.blocked
                    logger.info(f"Пользователь с telegram_id = {user_obj.telegram_id} заблокирован")
                else:
                    logger.info(
                        f"Количество оставшихся у пользователя с telegram_id = {user_obj.telegram_id} попыток: {3 - user_obj.number_of_attempts}")

                # Сохраняем изменения
                await request.commit()
            else:
                logger.warning(f"Пользователь с telegram_id = {user.telegram_id} не найден")

    @staticmethod
    async def update_number_of_attempts(user: UserAccess):
        """Обновляет количество попыток авторизаций у пользователя"""
        async with db.Session() as request:
            user_obj = await request.get(UserAccess, user.id)
            user_obj.number_of_attempts = user_obj.number_of_attempts + 1
            logger.info(f"У пользователя с telegram_id = {user.telegram_id}, было обновлено количество попыток")
            await request.commit()
            await UserAccessUpdater.update_user_status(user)


class SchedulerTasksUpdater:
    @staticmethod
    async def update_params(task: SchedulerTasks, time: datetime.datetime | None = None,
                            status: SchedulerStatus | None = None):
        """В зависимости от параметров может изменять статус и время задачи в таблице scheduler_tasks"""
        async with db.Session() as request:
            task_obj = await request.get(SchedulerTasks, task.id)
            if status:
                task_obj.status = status
                logger.info(f"У задачи {task_obj.id} был изменен статус на {status}")

            if time:
                task_obj.expected_completion_time = time
                logger.info(f"У задачи {task_obj.id} было изменено ожидаемое время выполнения {time}")

            await request.commit()


class ReportUpdater:
    @staticmethod
    async def update_params(report: Report, status: FinalStatus, comment: str) -> None:
        async with db.Session() as request:
            report_obj = await request.get(Report, report.id)

            report_obj.status = status.value
            logger.info(f"В отчете: №{report_obj.id} был изменен статус на {status.value}")
            report_obj.comment = comment
            logger.info(f"В отчете: №{report_obj.id} был изменен комментарий на {comment}")

            await request.commit()
