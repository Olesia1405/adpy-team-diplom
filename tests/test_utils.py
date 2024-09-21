"""
В тестах используются мок-объекты (MagicMock) для симуляции методов VKAPI и базы данных, чтобы изолировать тестируемый функционал.
Проверяются ключевые сценарии, такие как успешное сохранение данных, извлечение фотографий и взаимодействие с базой данных.
"""

import pytest
from unittest.mock import MagicMock

from utils import AuxiliaryUtils, DatabaseUtils

# Тестирование метода prepare_user_candidate_data
def test_prepare_user_candidate_data():
    utils = AuxiliaryUtils()
    
    # Мокирование методов VKAPI
    utils.vk_service.get_users_info = MagicMock(return_value={
        'id': 123,
        'first_name': 'John',
        'last_name': 'Doe',
        'city': 'Moscow',
        'bdate': '1990-01-01',
        'sex': 2
    })
    utils.vk_service.get_top_photos = MagicMock(return_value=['https://vk.com/photo123_456'])
    
    # Мокирование методов DatabaseUtils
    utils.db_utils.insert_data = MagicMock(return_value=1)
    
    # Вызов функции
    result = utils.prepare_user_candidate_data(user_vk_id=123)
    
    # Проверка результата
    assert result == 'Регистрация прошла успешно✅'
    utils.vk_service.get_users_info.assert_called_once_with(123)
    utils.vk_service.get_top_photos.assert_called_once_with(123)
    utils.db_utils.insert_data.assert_called_once()

# Тестирование метода _extract_photo_attachment
def test_extract_photo_attachment():
    utils = AuxiliaryUtils()
    photo_urls = ['https://vk.com/photo123_456', 'https://vk.com/photo789_101']
    result = utils._extract_photo_attachment(photo_urls)
    assert result == ['photo123_456', 'photo789_101']

    # Проверка, что функция возвращает None для неправильного URL
    photo_urls_invalid = ['https://vk.com/photo_invalid']
    result_invalid = utils._extract_photo_attachment(photo_urls_invalid)
    assert result_invalid is None


# Тестирование метода check_user_existence_db
def test_check_user_existence_db():
    db_utils = DatabaseUtils()
    db_utils.select_data = MagicMock(return_value=123)
    
    # Вызов метода
    result = db_utils.check_user_existence_db(123)
    
    # Проверка результата
    assert result == 123
    db_utils.select_data.assert_called_once()

# Тестирование метода seve_user_candidate
def test_save_user_candidate():
    db_utils = DatabaseUtils()
    data = {'vk_id': 123, 'name': 'John Doe', 'city': 'Moscow'}
    db_utils.insert_data = MagicMock(return_value=1)
    
    # Вызов метода
    result = db_utils.seve_user_candidate(data)
    
    # Проверка результата
    assert result == 1
    db_utils.insert_data.assert_called_once_with(table_name='users', data=data)