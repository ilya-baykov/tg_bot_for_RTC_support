from main_objects import db


class EmployeesUpdater:

    @staticmethod
    async def update_status(employee, status):
        """Изменяет статус сотрудника"""
        async with db.Session() as request:
            # Получаем сотрудника
            employee = await request.merge(employee)

            # Вносим изменения в статус
            employee.status = status

            # Сохраняем изменения
            await request.commit()


class ActionsUpdater:
    @staticmethod
    async def update_status(action, status):
        """Изменяет статус действия"""
        async with db.Session() as request:
            # Получаем действие
            action = await request.merge(action)

            # Вносим изменения в статус
            action.status = status

            # Сохраняем изменения
            await request.commit()
