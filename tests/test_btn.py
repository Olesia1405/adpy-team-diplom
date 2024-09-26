"""
test_button_constants: Проверяет, что текстовые метки для кнопок заданы корректно.
test_buttons_regist: Проверяет список кнопок для регистрации, включая текст и цвет.
test_buttons_start: Проверяет список кнопок для стартового экрана.
test_buttons_choice: Проверяет список кнопок для выбора действия ("Нравится", "Не нравится", "Следующий").
test_buttons_choice_sex: Проверяет кнопки для выбора пола.
test_welcome_message: Проверяет корректность приветственного сообщения.
"""

import pytest
from vk_api.keyboard import VkKeyboardColor
from btn_text import (
    BTN_REGISTRATION, BTN_FIND_PAIR, BTN_HELP, BTN_LIKE, BTN_DISLIKE,
    BTN_SEX_MAN, BTN_SEX_WOMAN, buttons_regist, buttons_start,
    buttons_choice, buttons_choice_sex, WELCOME_MESSAGE, BTN_CHOSEN, BTN_MAIN_MENU, BTN_NEXT, BTN_BACK,
    BTN_REMOVE_FAVORITES, buttons_favorites, buttons_favorites_next, buttons_favorites_back, HELP_MESSAGE
)


# Тестируем константы для названий кнопок
def test_button_constants():
    assert BTN_REGISTRATION == 'Начать регистрацию📋'
    assert BTN_FIND_PAIR == "Найти пару💓"
    assert BTN_HELP == "Помощь🆘"
    assert BTN_LIKE == "Нравится👍"
    assert BTN_DISLIKE == "Не нравится👎"
    assert BTN_SEX_MAN == 'Кавалера🙎‍♂️'
    assert BTN_SEX_WOMAN == 'Женщину🙎‍♀️️'
    assert BTN_MAIN_MENU == 'Главное меню🏠'
    assert BTN_CHOSEN == "⭐Избранные⭐"
    assert BTN_NEXT == 'Следующий🔜'
    assert BTN_BACK == 'Предыдущий🔙'
    assert BTN_REMOVE_FAVORITES == 'Убрать из избранных💔'


# Тестируем списки кнопок и их цвета
def test_buttons_regist():
    assert buttons_regist == [
        (BTN_REGISTRATION, VkKeyboardColor.POSITIVE),
        (BTN_HELP, VkKeyboardColor.NEGATIVE)
    ]


def test_buttons_start():
    assert buttons_start == [
        (BTN_FIND_PAIR, VkKeyboardColor.PRIMARY),
        (BTN_CHOSEN, VkKeyboardColor.POSITIVE),
        (BTN_HELP, VkKeyboardColor.NEGATIVE)
    ]


def test_buttons_choice():
    assert buttons_choice == [
        (BTN_LIKE, VkKeyboardColor.POSITIVE),
        (BTN_DISLIKE, VkKeyboardColor.NEGATIVE),
        (BTN_MAIN_MENU, VkKeyboardColor.PRIMARY)
    ]


def test_buttons_choice_sex():
    assert buttons_choice_sex == [
        (BTN_SEX_MAN, VkKeyboardColor.PRIMARY),
        (BTN_SEX_WOMAN, VkKeyboardColor.POSITIVE),
        (BTN_MAIN_MENU, VkKeyboardColor.PRIMARY)
    ]


def test_buttons_favorites():
    assert buttons_favorites == [(BTN_BACK, VkKeyboardColor.PRIMARY),
                                 (BTN_NEXT, VkKeyboardColor.PRIMARY),
                                 (BTN_REMOVE_FAVORITES, VkKeyboardColor.NEGATIVE),
                                 (BTN_MAIN_MENU, VkKeyboardColor.POSITIVE)
                                 ]


def test_buttons_favorites_next():
    assert buttons_favorites_next == [(BTN_NEXT, VkKeyboardColor.PRIMARY),
                                      (BTN_REMOVE_FAVORITES, VkKeyboardColor.NEGATIVE),
                                      (BTN_MAIN_MENU, VkKeyboardColor.POSITIVE)
                                      ]


def test_buttons_favorites_back():
    assert buttons_favorites_back == [(BTN_BACK, VkKeyboardColor.PRIMARY),
                                      (BTN_REMOVE_FAVORITES, VkKeyboardColor.NEGATIVE),
                                      (BTN_MAIN_MENU, VkKeyboardColor.POSITIVE)
                                      ]


# Тестируем welcome_message
def test_welcome_message():
    expected_message = (
        '\nДобро пожаловать в наш бот для поиска своей второй половинки 💕! \n\n'
        'Мы поможем тебе найти интересных людей и завести новые знакомства.\n\n'
        'Нажми "Найти пару 💓", чтобы начать поиск! Если что-то непонятно — '
        'всегда можно нажать на "Помощь 🆘".\n\n'
        'Удачи в поиске, надеемся, что здесь ты найдёшь именно того, кого ищешь! 💫'
    )
    assert WELCOME_MESSAGE == expected_message


def test_help_message():
    expected_message = (
                """
                Этот бот поможет вам найти пару! 👫
                
                Команды бота:
                - "Начать" — зарегистрируйтесь и начните поиск.
                - "Найти пару" — выберите параметры для поиска кандидатов.
                - "Помощь" — получите информацию о командах бота.
                
                Используйте кнопки на клавиатуре для быстрого доступа к функциям.
                
                Если возникли вопросы, обратитесь в поддержку. Удачи в поиске!
                """
    )
    assert HELP_MESSAGE == expected_message
