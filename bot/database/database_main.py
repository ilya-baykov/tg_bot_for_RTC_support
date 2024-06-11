from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Annotated
from bot.database.config import settings

engine = create_engine(
    url=settings.DATABASE_URL,
    echo=True
)

session_factory = sessionmaker(engine)

str_50 = Annotated[str, 50]
str_100 = Annotated[str, 100]
str_512 = Annotated[str, 512]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_50: String(50),
        str_100: String(100),
        str_512: String(512),
    }
