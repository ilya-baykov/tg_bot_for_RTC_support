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


class ErrorTypes(enum.Enum):
    robot_error = "Ошибка робота (плохая отказоустойчивость, невыполнение действий ТЗ, несвоевременная остановка))"
    startup_error = "Ошибка запуска (Проблемы ВМ, оркестратора, координатора)	"
    business_error = "Бизнес ошибка (входные данные, пользователь, изменение БП)"
    infrastructure_error = "Инфраструктурная ошибка (сбой систем, доступов, серверов)"
