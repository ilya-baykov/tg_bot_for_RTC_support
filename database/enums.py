import enum


class IntervalType(enum.Enum):
    every_day = "Каждый день"
    once_month = "Раз в месяц"
    one_time = "Однократное выполнение"


class ActionStatus(enum.Enum):
    queued_to_be_added = "В очереди на добавление в обработку"
    waiting_to_be_sent = "Ожидает отправки сообщения"
    sent = "Сообщение отправлено"
    completed = "Сообщение обработано сотрудником"


class EmployeesStatus(enum.Enum):
    available = "Свободен"
    busy = "Занят"


class FinalStatus(enum.Enum):
    successfully = "Успешно"
    failed = "провалено"
