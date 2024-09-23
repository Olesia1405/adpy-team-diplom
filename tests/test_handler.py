"""
test_message_handler_start_new_user: Тестирует логику для нового пользователя при вводе команды "начать".
test_message_handler_start_registered_user: Тестирует логику для зарегистрированного пользователя.
test_message_handler_registration: Тестирует реакцию на команду регистрации.
test_state_handler_waiting_for_sex: Тестирует обработку состояния "ожидание выбора пола".
test_state_handler_waiting_for_age: Тестирует обработку состояния "ожидание ввода возраста".
test_state_handler_waiting_for_city: Тестирует обработку состояния "ожидание ввода города".
"""

import pytest
from unittest.mock import MagicMock
from handler import Handler
from unittest.mock import patch
from unittest.mock import patch, MagicMock

from btn_text import buttons_regist, buttons_start, \
    buttons_choice_sex, BTN_REGISTRATION, BTN_FIND_PAIR, BTN_SEX_MAN, welcome_message

# Пример фикстуры для мока объекта VKBot
@pytest.fixture
def mock_vk_bot():
    vk_bot = MagicMock()
    vk_bot.send_message = MagicMock()
    vk_bot.create_keyboard = MagicMock(return_value='keyboard_mock')
    vk_bot.set_user_state = MagicMock()
    return vk_bot

# Пример фикстуры для мока базы данных
@pytest.fixture
def mock_db_utils():
    db_utils = MagicMock()
    db_utils.check_user_existence_db = MagicMock(return_value=None)
    return db_utils

@pytest.fixture
def handler(mock_vk_bot, mock_db_utils):
    handler = Handler(mock_vk_bot)
    handler.util_db = mock_db_utils
    return handler

# Тестируем метод message_handler с командой "начать"
def test_message_handler_start_new_user(handler, mock_vk_bot):
    # Входные данные
    event = MagicMock()
    event.user_id = 123
    request = "начать"
    user_name = "Иван"

    # Вызов метода
    handler.message_handler(event, user_name, request)

    # Проверяем, что методы send_message и create_keyboard вызываются с ожидаемыми аргументами
    mock_vk_bot.send_message.assert_called_with(
        123, f"Привет, {user_name}! 👋 {welcome_message}",
        keyboard='keyboard_mock'
    )
    mock_vk_bot.create_keyboard.assert_called_with(buttons_regist)

# Тестируем метод message_handler для зарегистрированного пользователя
def test_message_handler_start_registered_user(handler, mock_vk_bot, mock_db_utils):
    # Настроим, чтобы база данных возвращала существующего пользователя
    mock_db_utils.check_user_existence_db.return_value = True

    # Входные данные
    event = MagicMock()
    event.user_id = 123
    request = "начать"
    user_name = "Иван"

    # Вызов метода
    handler.message_handler(event, user_name, request)

    # Проверяем, что для зарегистрированного пользователя отправляется корректное сообщение
    mock_vk_bot.send_message.assert_called_with(
        123, f"Привет, {user_name}! 👋",
        keyboard='keyboard_mock'
    )
    mock_vk_bot.create_keyboard.assert_called_with(buttons_start)

# Тестируем метод message_handler с запросом на регистрацию
def test_message_handler_registration(handler, mock_vk_bot):
    # Входные данные
    event = MagicMock()
    event.user_id = 123
    request = BTN_REGISTRATION.lower()
    user_name = "Иван"

    handler.utils_auxiliary.prepare_user_candidate_data = MagicMock(return_value="тестовые данные")

    # Вызов метода
    handler.message_handler(event, user_name, request)

    # Проверяем, что бот отправляет сообщение с подготовленными данными
    mock_vk_bot.send_message.assert_called_with(
        123, f"{user_name} тестовые данные",
        keyboard='keyboard_mock'
    )
    mock_vk_bot.create_keyboard.assert_called_with(buttons_start)

# Тестируем state_handler с состоянием "waiting_for_sex"
def test_state_handler_waiting_for_sex(handler, mock_vk_bot):
    # Входные данные
    event = MagicMock()
    user_id = 123
    user_name = "Иван"
    state = "waiting_for_sex"
    request = BTN_SEX_MAN.lower()

    # Вызов метода
    handler.state_handler(state, event, user_id, user_name, request)

    # Проверяем, что бот отправляет запрос на возраст и устанавливает новое состояние
    mock_vk_bot.send_message.assert_called_with(
        user_id, "Введите возраст или укажите диапазон возрастов, разделяя значения запятой."
    )
    mock_vk_bot.set_user_state.assert_called_with(user_id, "waiting_for_age")
    assert handler.user_data[user_id]['sex'] == 2  # Пол: мужской

# Тестируем state_handler с состоянием "waiting_for_age"
def test_state_handler_waiting_for_age(handler, mock_vk_bot):
    # Входные данные
    event = MagicMock()
    user_id = 123
    user_name = "Иван"
    state = "waiting_for_age"
    request = "25,30"

    # Устанавливаем начальные данные пользователя
    handler.user_data[user_id] = {}

    # Вызов метода
    handler.state_handler(state, event, user_id, user_name, request)

    # Проверяем, что бот отправляет запрос на город и обновляет возраст
    mock_vk_bot.send_message.assert_called_with(user_id, "Укажите город в котором искать спутника жизни")
    mock_vk_bot.set_user_state.assert_called_with(user_id, "waiting_for_city")
    assert handler.user_data[user_id]['age'] == ['25', '30']

# Тестируем state_handler с состоянием "waiting_for_city"
from unittest.mock import patch, MagicMock

# Тестируем state_handler с состоянием "waiting_for_city"
# Тестируем state_handler с состоянием "waiting_for_city"
@patch('utils.AuxiliaryUtils.get_candidate_db')  # Патч для get_candidate_db
@patch.object(Handler, 'message_handler')  # Патч для message_handler
def test_state_handler_waiting_for_city(mock_message_handler, mock_get_candidate_db, handler, mock_vk_bot):
    # Патчим метод set_user_state на объекте vk_bot
    handler.vk_bot.set_user_state = MagicMock()

    # Входные данные
    event = MagicMock()
    user_id = 123
    user_name = "Иван"
    state = "waiting_for_city"
    request = "Москва"

    # Устанавливаем начальные данные пользователя
    handler.user_data[user_id] = {}

    # Инициализация user_candidate_data для пользователя
    handler.user_candidate_data[user_id] = {}  # Добавляем пустой словарь

    # Вызов метода
    handler.state_handler(state, event, user_id, user_name, request)

    # Проверяем, что данные о городе обновляются
    assert handler.user_data[user_id]['city'] == request  # Проверка, что город установлен в "Москва"

    # Проверяем, что set_user_state был вызван
    handler.vk_bot.set_user_state.assert_called_with(user_id, None)

    # Проверяем, что message_handler был вызван с правильными аргументами
    mock_message_handler.assert_called_once_with(event, user_name, 'show')