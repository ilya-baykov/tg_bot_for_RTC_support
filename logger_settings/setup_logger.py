from logging import getLogger, basicConfig, DEBUG, FileHandler, StreamHandler
from datetime import datetime
import os

LOG_FORMAT = '%(asctime)s : %(name)s : %(levelname)s : %(message)s'
LOGS_DIR = os.getenv("LOGS_PATH", "define me!")  # получаем путь к папке LOGS
os.makedirs(LOGS_DIR, exist_ok=True)  # Проверка наличия папки (при ее отсуствии - создание)


def setup_logger():
    logger = getLogger()
    # Запись в файл
    log_file_path = os.path.join(LOGS_DIR, f"Logger_{datetime.today().strftime('%d_%m_%Y')}.log")
    file_handler = FileHandler(log_file_path, mode="a")
    file_handler.setLevel(DEBUG)

    # Запись в консоль
    console_handler = StreamHandler()
    console_handler.setLevel(DEBUG)
    basicConfig(level=DEBUG, format=LOG_FORMAT, handlers=[file_handler, console_handler])
    return logger
