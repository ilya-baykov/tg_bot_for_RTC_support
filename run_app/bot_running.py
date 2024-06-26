from aiogram import Dispatcher

from handlers.edit.edit_report_task import register_edit_handlers
from handlers.processing_employee_responses.employee_responses import register_user_response
from handlers.start.registration import register_start_handlers
from handlers.unknown_commands.unknown_response import register_unknown_command
from main_objects import bot

dp = Dispatcher()


async def start_bot():
    # Регистрация обработчиков

    register_start_handlers(dp)  # Стартовый обработчик
    register_edit_handlers(dp)  # Обработчик для редактирования отчетов
    register_user_response(dp)  # Обработчик ответов сотрудников
    register_unknown_command(dp)  # Обработчик неизвестных команд

    await dp.start_polling(bot, skip_updates=True)
