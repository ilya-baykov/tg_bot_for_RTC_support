import re

from aiogram.filters import Filter
from aiogram.types import Message


# class MyFilter(Filter):
#
#     async def __call__(self, message: Message) -> bool:
#         pattern = r"Имя процесса: (.*)\nОписание процесса: (.*)"
#         return bool(re.match(pattern, message.text)) and message.from_user.id == "7405453506"
