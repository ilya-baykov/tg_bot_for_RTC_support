import asyncio
from collections import defaultdict

from handlers.send_task_notifications.keyboard import keyboard


class TaskManager:
    def __init__(self, bot, db):
        self.bot = bot  # Экземпляр Telegram бота
        self.db = db  # Экземпляр класса для работы с БД
        self.task_queues = defaultdict(asyncio.Queue)  # Словарь очередей задач для каждого сотрудника

    async def load_tasks(self):
        # Загружает будущие задачи из базы данных
        tasks = await self.db.select_future_tasks()
        for task in tasks:
            # Получаем сотрудника по его Telegram username
            employee = await self.db.get_employee_by_telegram_username(task.employee_telegram)
            if employee:
                # Добавляем задачу в очередь соответствующего сотрудника
                await self.task_queues[employee.employee_id].put(task)
        for employee_id, queue in self.task_queues.items():
            # Запускаем асинхронную задачу для обработки очереди задач сотрудника
            await asyncio.create_task(self.process_tasks(employee_id, queue))

    async def process_tasks(self, employee_id, queue):
        while True:
            # Получаем следующую задачу из очереди, если она есть
            try:
                task = queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            try:
                # Отправляем уведомление о задаче сотруднику
                await self.send_task_notification(employee_id, task)

                # # Ожидаем ответа от сотрудника
                # response = await self.wait_for_response(employee_id)
                # # Обновляем статус задачи в базе данных
                # await self.db.update_task_status(task.entry_id, response)
            except Exception as e:
                print(f"Error processing task for employee {employee_id}: {e}")
            finally:
                # Уведомляем очередь, что задача завершена
                queue.task_done()

    async def send_task_notification(self, employee_id, task):
        # Получаем данные сотрудника по его ID
        employee = await self.db.get_employee_by_telegram_username(task.employee_telegram)
        # Получаем данные процесса по имени процесса
        process = await self.db.get_process_by_name(task.process_name)
        # Формируем текст сообщения
        message_text = (
            f"Привет, {employee.name}!\n"
            f"Ваша задача: {process.process_name}\n"
            f"Описание: {process.action_description}\n"
            f"Запланировано на: {task.scheduled_time}"
        )
        # Отправляем сообщение сотруднику в Telegram
        await self.bot.send_message(chat_id=employee.telegram_id, text=message_text, reply_markup=keyboard)

    async def wait_for_response(self, employee_id):
        # Логика ожидания ответа от сотрудника
        # Может быть реализация с использованием async или событий
        pass
