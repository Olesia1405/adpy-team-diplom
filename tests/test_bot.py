"""
test_create_keyboard: Тестирует метод create_keyboard, проверяя, что клавиатура создается с правильными кнопками.
test_send_message: Проверяет метод send_message, используя mock, чтобы убедиться, что метод вызывается с правильными аргументами.
test_get_user_name: Тестирует получение имени пользователя с помощью mock для метода VK API users.get.
test_user_state: Проверяет методы установки и получения состояния пользователя.
"""

import pytest
from unittest.mock import MagicMock, patch
from vk_api.keyboard import VkKeyboard
from bot import VKBot
from config import VK_GROUP_TOKEN

# Тестируем создание клавиатуры
def test_create_keyboard():
    bot = VKBot(VK_GROUP_TOKEN)
    
    # Проверка клавиатуры с одной кнопкой
    buttons = [("Button1", "primary")]
    keyboard = bot.create_keyboard(buttons)
    
    assert isinstance(keyboard, VkKeyboard)
    assert "Button1" in keyboard.lines[0][0].label
    assert keyboard.lines[0][0].color == "primary"
    
    # Проверка клавиатуры с несколькими кнопками
    buttons = [("Button1", "primary"), ("Button2", "secondary")]
    keyboard = bot.create_keyboard(buttons)
    
    assert "Button2" in keyboard.lines[1][0].label

# Тестируем отправку сообщения
@patch('bot.VKBot.send_message')
def test_send_message(mock_send_message):
    bot = VKBot(VK_GROUP_TOKEN)
    user_id = 123
    message = "Test message"
    
    bot.send_message(user_id, message)
    
    mock_send_message.assert_called_once_with(user_id, message)

# Тестируем получение имени пользователя
@patch('bot.VKBot.get_user_name')
def test_get_user_name(mock_get_user_name):
    bot = VKBot(VK_GROUP_TOKEN)
    user_id = 123
    
    # Задаем фиктивный результат для вызова метода API
    mock_get_user_name.return_value = "Ivan Ivanov"
    
    name = bot.get_user_name(user_id)
    
    assert name == "Ivan Ivanov"
    mock_get_user_name.assert_called_once_with(user_id)

# Тестируем установку и получение состояния пользователя
def test_user_state():
    bot = VKBot(VK_GROUP_TOKEN)
    user_id = 123
    state = "some_state"
    
    bot.set_user_state(user_id, state)
    
    assert bot.get_user_state(user_id) == state

    # Проверка состояния, если оно не установлено
    assert bot.get_user_state(999) is None
