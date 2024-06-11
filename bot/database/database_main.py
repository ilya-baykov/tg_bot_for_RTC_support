from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, registry

from bot.database.config import settings
from bot.database.models.type_annotation_map import *

engine = create_engine(
    url=settings.DATABASE_URL,
    echo=True
)

session_factory = sessionmaker(engine)


# Базовый класс с использованием аннотированных типов
# class Base(DeclarativeBase):
#     registry = registry(
#         type_annotation_map={
#             str_50: String(50),
#             str_100: String(100),
#         }
#     )
class Base(DeclarativeBase):
    pass
