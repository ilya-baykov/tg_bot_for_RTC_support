# import datetime
# import enum
#
# from sqlalchemy import String, DateTime, Text
# from sqlalchemy.sql.annotation import Annotated
# from sqlalchemy.orm import mapped_column
#
# # Определяем аннотированные типы
# str_50 = Annotated[str, 50]
# str_100 = Annotated[str, 100]
#
# intpk = Annotated[int, mapped_column(primary_key=True)]
# text = Annotated[str, mapped_column(Text, nullable=False)]
# DateTimeNotNull = Annotated[datetime.datetime, mapped_column(DateTime, nullable=False)]
#
#
# class Status(enum.Enum):
#     ok = "ОК"
#     not_ok = "НЕ ОК"
