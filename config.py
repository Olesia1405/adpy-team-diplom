import os
import logging
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные окружения из файла .env

# Настройки базы данных
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Токены группы и API VK
VK_API_TOKEN = os.getenv('VK_API_TOKEN')
VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')


# Версия VK API
VK_API_VERSION = '5.131'


def config_logging(level=logging.INFO):
    """
        Настройка логирования для приложения.
        :param level: Уровень логирования. По умолчанию - INFO.
    """

    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)10s - %(message)s"

    )
    logger = logging.getLogger(__name__)
    logger.info(f"Текущий уровень логгирования: {logger.getEffectiveLevel()}")
