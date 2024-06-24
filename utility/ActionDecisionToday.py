import logging
import calendar
import re
from datetime import datetime

from database.enums import IntervalType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DAYS_OF_WEEK_EN_RU = {
    'monday': ('понедельник', 'пн'),
    'tuesday': ('вторник', 'вт'),
    'wednesday': ('среда', 'ср'),
    'thursday': ('четверг', 'чт'),
    'friday': ('пятница', 'пт'),
    'saturday': ('суббота', 'сб'),
    'sunday': ('воскресенье', 'вскр'),
}


class ActionDecisionToday:
    def __init__(self, interval: IntervalType, day_of_action: str | None, task_id: int):
        self.interval = interval
        self.day_of_action = day_of_action
        self.task_id = task_id
        self.current_time = datetime.now()
        self.decision_func = self.choose_decision_func()

    def choose_decision_func(self):
        return {
            IntervalType.ежедневно: self.daily_tasks_decision(),
            IntervalType.еженедельно: self.weekly_tasks_decision(),
            IntervalType.ежемесячно: self.monthly_tasks_decision(),
            IntervalType.разово: self.one_time_tasks_decision(),
        }

    def daily_tasks_decision(self):
        return True

    def weekly_tasks_decision(self):
        day_of_week_eng = self.current_time.strftime('%A')  # Получаем название дня недели
        return self.day_of_action.lower() in DAYS_OF_WEEK_EN_RU[day_of_week_eng.lower()]

    def monthly_tasks_decision(self):
        # Если день активации указан числом
        if self.day_of_action.isdigit():
            return self.day_of_action.isdigit() and int(self.day_of_action) == self.current_time.day

        elif self.day_of_action == "последний":
            # Получаем количество дней в этом месяце
            last_day_month = calendar.monthrange(self.current_time.year, self.current_time.month)[1]
            return self.current_time.day == last_day_month
        else:
            # Для ежемесячных задач с периодам выполнения (пример: c 12 по 29  в виде '12-29' )
            regex_pattern = r"\b([1-9]|[12][0-9]|3[01])\s*-\s*\b([1-9]|[12][0-9]|3[01])\b$"
            clean_day_of_action = re.sub(r'\s+', ' ', self.day_of_action.strip())
            # Проверка правильности формата
            if re.match(regex_pattern, clean_day_of_action):
                days_interval = clean_day_of_action.split("-")
                if len(days_interval) == 2 and int(days_interval[0]) < int(days_interval[1]):
                    return int(days_interval[0]) < self.current_time.day < int(days_interval[1])

            return False

    def one_time_tasks_decision(self):
        regex_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if regex_pattern.match(self.day_of_action):
            try:
                action_date = datetime.strptime(self.day_of_action, '%Y-%m-%d').date()
                current_date = self.current_time.date()
                return current_date == action_date
            except ValueError:
                pass
        return False
