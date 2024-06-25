import asyncio

from aiogram.fsm.storage.redis import RedisStorage


async def start():
    storage = RedisStorage.from_url('radis://localhost:6379/0')

    await storage.redis.ser(name=123456789, value=1, ex=10)

    for i in range(15):
        value = await storage.redis.get(name=123456789)

        if value:
            print("Значение есть")
        else:
            print("Значения нет")
            break


asyncio.run(start())
