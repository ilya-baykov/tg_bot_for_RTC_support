from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import Annotated

str_50 = Annotated[str, 50]
str_100 = Annotated[str, 100]
str_512 = Annotated[str, 512]


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        str_50: String(50),
        str_100: String(100),
        str_512: String(512),
    }
