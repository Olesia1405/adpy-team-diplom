import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные окружения из файла .env

# Настройки базы данных
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Токен группы VK
VK_TOKEN = os.getenv('VK_TOKEN')

# Версия VK API
VK_API_VERSION = '5.131'
