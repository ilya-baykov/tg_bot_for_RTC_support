import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.CRUD.read import UserAccessReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IsTrueContact(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        try:
            return message.contact.user_id == message.from_user.id
        except:
            return False





