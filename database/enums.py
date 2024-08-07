import enum


class UserStatus(enum.Enum):
    blocked = "Заблокирован"
    available = "Досупен"


class IntervalType(enum.Enum):
    ежедневно = "Каждый день"
    еженедельно = "Каждую неделю"
    ежемесячно = "Раз в месяц"
    разово = "Однократное выполнение"


class ActionStatus(enum.Enum):
    queued_to_be_added = "В очереди на добавление в обработку"
    waiting_to_be_sent = "Ожидает отправки сообщения"
    sent = "Сообщение отправлено"
    completed = "Сообщение обработано сотрудником"
    postponed = "Отложено"


class EmployeesStatus(enum.Enum):
    available = "Свободен"
    busy = "Занят"


class FinalStatus(enum.Enum):
    successfully = "Успешно"
    failed = "Отклонено"


class SchedulerStatus(enum.Enum):
    awaiting_dispatch = "Ожидает отправки"
    successfully = "Успешно выполнено"
    suspended = "Приостановлено"


class Priority(enum.Enum):
    Высокий = "Высокий приоритет"
    Средний = "Средний приоритет"
    Низкий = "Низкий приоритет"
