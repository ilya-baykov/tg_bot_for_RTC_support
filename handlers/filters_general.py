import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.CRUD.read import EmployeesReader, UserAccessReader

logger = logging.getLogger(__name__)


class RegisteredUser(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        employee = await EmployeesReader().get_employee_by_telegram_id_or_username(
            telegram_id=str(message.from_user.id))
        if employee:
            return True
        logger.info(
            f"Незарегистрированный пользователь с telegram_id = {message.from_user.id} пытался взаимодействовать с ботом ")
        return False


class UserInBanList(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        verdict = await UserAccessReader.is_block_user(telegram_id=str(message.from_user.id))
        if verdict:
            logger.info(
                f"Заблокированнй пользователь с telegram_id = {message.from_user.id} пытался взаимодействовать с ботом ")
            return True
        return False
