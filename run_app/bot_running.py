from aiogram import Dispatcher

from handlers.add_journal_entry.add_operation_log import register_add_operation_log_handler
from handlers.edit.edit_report_task import register_edit_handlers
from handlers.postponed.deferred_processes import register_postponed_handlers
from handlers.processing_employee_responses.employee_responses import register_user_response
from handlers.start.registration import register_start_handlers
from handlers.unknown_commands.unknown_response import register_unknown_command
from main_objects import bot
# from take_photo.state import register_photo_by_user

dp = Dispatcher()


async def start_bot():
    # Регистрация обработчиков

    register_start_handlers(dp)  # Стартовый обработчик
    # register_photo_by_user(dp)
    register_postponed_handlers(dp)  # Обработчик отложенных процессов
    register_edit_handlers(dp)  # Обработчик для редактирования отчетов
    register_user_response(dp)  # Обработчик ответов сотрудников
    register_add_operation_log_handler(dp)  # Обработчик для добавления записей в журнал эксплуатации
    register_unknown_command(dp)  # Обработчик неизвестных команд

    await dp.start_polling(bot, skip_updates=True)

