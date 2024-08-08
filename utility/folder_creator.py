import os

SCREENSHOTS_PATH = os.environ.get("SCREENSHOTS_PATH", default="define SCREENSHOTS_PATH")


class FolderCreator:
    """Класс для создания папок для хранения скриншотов сотрудников"""

    # Получить название процесса
    # Получить фамилию сотрудника
    # os.makedirs('a/very/deep/path/to/new_folder', exist_ok=True)

    def __init__(self, process_name: str, employee_name):
        """Принимает для инициализации имя процесса и ФИО сотрудника"""
        self.process_name = process_name
        self.employee = employee_name

    def create_path(self):
        os.makedirs(f"{SCREENSHOTS_PATH}\\{self.process_name}")
