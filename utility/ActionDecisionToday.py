import logging
import calendar
import re
from datetime import datetime

from abc import ABC, abstractmethod

from database.enums import IntervalType

DAYS_OF_WEEK_EN_RU = {
    'monday': ('понедельник', 'пн'),
    'tuesday': ('вторник', 'вт'),
    'wednesday': ('среда', 'ср'),
    'thursday': ('четверг', 'чт'),
    'friday': ('пятница', 'пт'),
    'saturday': ('суббота', 'сб'),
    'sunday': ('воскресенье', 'вскр'),
}


class DecisionFunc(ABC):

    def __init__(self, day_of_action: str):
        self.day_of_action = day_of_action
        self.current_time = datetime.now()

    @abstractmethod
    def make_decision(self) -> bool:
        pass


class ActionDecisionToday:
    """Класс для принятия решения по задаче на текущий день."""

    def __init__(self, interval: IntervalType, day_of_action: str | None):
        """
        Инициализация объекта для принятия решения по задаче на текущий день.

        Args:
            interval (IntervalType): Тип интервала задачи.
            day_of_action (str | None): День или дата, связанная с задачей.
        """
        self.interval = interval
        self.day_of_action = day_of_action
        self.decision_func = self.choose_decision_func()

    def choose_decision_func(self) -> DecisionFunc:
        """
        Выбирает функцию для принятия решения на основе типа интервала задачи.

        Returns:
            Callable[[], bool]: Функция для принятия решения.
        """
        if self.interval == IntervalType.ежедневно:
            return DailyDecision(self.day_of_action)
        elif self.interval == IntervalType.еженедельно:
            return WeeklyDecision(self.day_of_action)
        elif self.interval == IntervalType.ежемесячно:
            return MonthlyDecision(self.day_of_action)
        elif self.interval == IntervalType.разово:
            return OneTimeDecision(self.day_of_action)
        else:
            raise ValueError("Unsupported interval type")

    def make_decision(self) -> bool:
        """
        Принимает решение на основе текущего времени и типа задачи.

        Returns:
            bool: Результат принятия решения (True или False).
        """
        return self.decision_func.make_decision()


class DailyDecision(DecisionFunc):
    """Класс для принятия решений для ежедневных задач."""

    def make_decision(self) -> bool:
        """Принимает решение для ежедневной задачи (всегда возвращает True)."""
        return True


class WeeklyDecision(DecisionFunc):
    """Класс для принятия решений для еженедельных задач."""

    def make_decision(self) -> bool:
        """Принимает решение для еженедельной задачи на основе текущего дня недели."""

        day_of_week_eng = self.current_time.strftime('%A')  # Текущий день недели на английском языке
        days = self.day_of_action.lower().split(',')  # Разбиваем строку из дней недели (пн,ср,пт) -пример
        for day in days:
            if day in DAYS_OF_WEEK_EN_RU[day_of_week_eng.lower()]:
                return True
        return False


class MonthlyDecision(DecisionFunc):
    """Класс для принятия решений для ежемесячных задач."""

    def make_decision(self) -> bool:
        """Принимает решение для ежемесячной задачи на основе текущей даты."""

        if self.day_of_action.isdigit():
            return int(self.day_of_action) == self.current_time.day
        elif self.day_of_action == "последний":
            last_day_month = calendar.monthrange(self.current_time.year, self.current_time.month)[1]
            return self.current_time.day == last_day_month
        elif "," in self.day_of_action:
            month_interval_days = self.day_of_action.split(',')  # Разбваем строку на интервалы или дни

            if "-" in self.day_of_action:
                # Пример: 12-22,26-29

                regex_pattern = r"\b([1-9]|[12][0-9]|3[01])\s*-\s*\b([1-9]|[12][0-9]|3[01])\b$"  # пример паттерна : 12-22

                for interval in month_interval_days:
                    clean_day_of_action = re.sub(r'\s+', ' ', interval.strip())  # Очищаем интервал от пробелов
                    if re.match(regex_pattern, clean_day_of_action):  # Проверяем интревал на соотвествие паттерну
                        days_interval = clean_day_of_action.split("-")  # Разбиваем интервал на два числа

                        # Проверяем текущий день в рамках интервала
                        if len(days_interval) == 2 and int(days_interval[0]) < int(days_interval[1]):
                            return int(days_interval[0]) < self.current_time.day < int(days_interval[1])
                return False
            else:
                # Пример: 13,17,19,22
                for interval in month_interval_days:
                    clean_day_of_action = re.sub(r'\s+', ' ', interval.strip())  # Очищаем интервал от пробелов
                    try:
                        # Пробуем перевести в число и сравнить с текущим днём
                        if int(clean_day_of_action) == self.current_time.day:
                            return True
                    except Exception:
                        pass
                return False


class OneTimeDecision(DecisionFunc):
    """Класс для принятия решений для разовых задач."""

    def make_decision(self) -> bool:
        """Принимает решение для разовой задачи на основе заданной даты."""

        regex_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if regex_pattern.match(self.day_of_action):
            try:
                action_date = datetime.strptime(self.day_of_action, '%Y-%m-%d').date()
                current_date = self.current_time.date()
                return current_date == action_date
            except ValueError:
                pass
        return False
