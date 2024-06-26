import time
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: int):
        self.limit = limit
        self.users = {}

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]
                       ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.users:
            if current_time - self.users[user_id] < self.limit:
                self.users[user_id] = current_time
                return await event.answer("Слишком много запросов. Пожалуйста, подождите.")

        self.users[user_id] = current_time
        return await handler(event, data)


def register_throttling_middleware(dp: Dispatcher, limit: int):
    dp.message.middleware(ThrottlingMiddleware(limit))
