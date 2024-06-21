from main_objects import db


class EmployeesUpdater:

    @staticmethod
    async def update_status(employee, status):
        async with db.Session() as request:
            # Получаем сотрудника
            employee = await request.merge(employee)

            # Вносим изменения в статус
            employee.status = status

            # Сохраняем изменения
            await request.commit()
