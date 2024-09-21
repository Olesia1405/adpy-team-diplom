"""
Тест загрузки переменных окружения:
Проверяет, что все необходимые переменные окружения не равны None.
Проверяет, что версия API совпадает с ожидаемой.

Тест настройки логирования:
Проверяет, что уровень логирования установлен корректно.
Проверяет, что сообщения логирования записываются как ожидается с помощью caplog.
"""

import os
import pytest
import logging
from dotenv import load_dotenv

from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, VK_API_TOKEN, VK_GROUP_TOKEN, VK_API_VERSION, config_logging

# Тестирование загрузки переменных окружения
def test_environment_variables():
    load_dotenv()  # Загружаем переменные окружения из .env файла

    assert DB_NAME is not None, "DB_NAME should not be None"
    assert DB_USER is not None, "DB_USER should not be None"
    assert DB_PASSWORD is not None, "DB_PASSWORD should not be None"
    assert DB_HOST is not None, "DB_HOST should not be None"
    assert DB_PORT is not None, "DB_PORT should not be None"
    assert VK_API_TOKEN is not None, "VK_API_TOKEN should not be None"
    assert VK_GROUP_TOKEN is not None, "VK_GROUP_TOKEN should not be None"
    assert VK_API_VERSION == '5.131', "VK_API_VERSION should be '5.131'"

# Тестирование настройки логирования
def test_config_logging(caplog):
    config_logging(logging.DEBUG)

    # Проверка, что уровень логирования установлен корректно
    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG

    # Проверка, что логирование работает
    with caplog.at_level(logging.INFO):
        logging.info("Test logging message")
    
    assert "Test logging message" in caplog.text
