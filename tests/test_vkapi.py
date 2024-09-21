"""
test_get_users_info_success — тестирует успешное получение информации о пользователе через метод get_users_info.
test_get_users_info_error — проверяет правильность обработки ошибок API.
test_get_top_photos_success — проверяет успешное получение топовых фотографий пользователя.
test_get_top_photos_no_photos — проверяет случай, когда у пользователя нет фотографий.
test_search_users_success — тестирует успешный поиск пользователей по заданным критериям.
test_search_users_error — проверяет обработку ошибки при поиске пользователей.

Каждый тест использует @patch, чтобы имитировать ответ от API с помощью мокированного объекта Mock, 
предотвращая реальный вызов к серверу.
"""

import pytest
from unittest.mock import patch, Mock
from vk_api_service import VKAPI


@pytest.fixture
def vkapi_instance():
    """Фикстура для создания экземпляра класса VKAPI"""
    return VKAPI()


@patch('requests.get')
def test_get_users_info_success(mock_get, vkapi_instance):
    """Тест успешного получения информации о пользователе"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'response': [{
            'id': 123,
            'first_name': 'John',
            'last_name': 'Doe',
            'city': {'title': 'Moscow'},
            'sex': 2,
            'bdate': '15.01.1990'
        }]
    }
    mock_get.return_value = mock_response

    result = vkapi_instance.get_users_info(123)
    
    assert result['id'] == 123
    assert result['first_name'] == 'John'
    assert result['last_name'] == 'Doe'
    assert result['city'] == 'Moscow'
    assert result['sex'] == 2
    assert result['bdate'] == '1990-01-15'


@patch('requests.get')
def test_get_users_info_error(mock_get, vkapi_instance):
    """Тест обработки ошибки API при получении информации о пользователе"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'error': {'error_code': 5, 'error_msg': 'User authorization failed'}
    }
    mock_get.return_value = mock_response

    result = vkapi_instance.get_users_info(123)
    
    assert result is None


@patch('requests.get')
def test_get_top_photos_success(mock_get, vkapi_instance):
    """Тест успешного получения топовых фотографий"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'response': {
            'items': [
                {'id': 1, 'owner_id': 123, 'likes': {'count': 50}},
                {'id': 2, 'owner_id': 123, 'likes': {'count': 30}},
                {'id': 3, 'owner_id': 123, 'likes': {'count': 40}}
            ]
        }
    }
    mock_get.return_value = mock_response

    result = vkapi_instance.get_top_photos(123, top_n=2)
    
    assert len(result) == 2
    assert result[0] == "https://vk.com/123?z=photo123_1/photo_feed123"
    assert result[1] == "https://vk.com/123?z=photo123_3/photo_feed123"


@patch('requests.get')
def test_get_top_photos_no_photos(mock_get, vkapi_instance):
    """Тест случая, когда у пользователя нет фотографий"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'response': {
            'items': []
        }
    }
    mock_get.return_value = mock_response

    result = vkapi_instance.get_top_photos(123, top_n=3)
    
    assert result is None


@patch('requests.get')
def test_search_users_success(mock_get, vkapi_instance):
    """Тест успешного поиска пользователей"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'response': {
            'items': [
                {'id': 1, 'first_name': 'John', 'last_name': 'Doe'},
                {'id': 2, 'first_name': 'Jane', 'last_name': 'Smith'}
            ]
        }
    }
    mock_get.return_value = mock_response

    result = vkapi_instance.search_users(age=[25, 30], gender=2, city_name='Moscow')
    
    assert len(result) == 2
    assert result[0] == 1
    assert result[1] == 2


@patch('requests.get')
def test_search_users_error(mock_get, vkapi_instance):
    """Тест обработки ошибки API при поиске пользователей"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'error': {'error_code': 5, 'error_msg': 'User authorization failed'}
    }
    mock_get.return_value = mock_response

    result = vkapi_instance.search_users(age=[25], gender=1, city_name='Moscow')
    
    assert result is None
