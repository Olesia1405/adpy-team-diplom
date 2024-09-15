"""
Объяснение изменений:
Конструктор __init__:

Добавлен параметр db_params для подключения к базе данных.
Создано подключение к базе данных и курсор для выполнения SQL-запросов.

Метод add_to_favorites:
Перенесён в класс AnotherVKBot и использует self.cursor и self.connection для взаимодействия с базой данных.
Логирует информацию о добавлении пользователя в таблицу users и в таблицу favorites.

Обработчик сообщений:
В методе handle_message, при вызове add_to_favorites, передаются примеры данных. В реальной ситуации вам нужно будет заменить "Имя пользователя" и "https://vk.com/id123456" на данные, полученные из VK API или других источников.

Запуск бота:
В if __name__ == '__main__': добавлены параметры подключения к базе данных и токен группы ВКонтакте. Убедитесь, что вы заменили значения в db_params и token на свои реальные данные.

Метод send_message_with_buttons:
Добавлен метод send_message_with_buttons для создания и отправки сообщения с кнопками.
Используется VkKeyboard для создания клавиатуры и get_random_id() для генерации уникального идентификатора сообщения.

Методы send_help_message и send_unknown_command_message:
Обновлены, чтобы использовать новый метод send_message_with_buttons для отправки сообщений с кнопками.

Метод send_message:
Сохранен для отправки сообщений без кнопок.
"""


import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from btn_text import BTN_FIND_PAIR, BTN_LIKE, BTN_NEXT, BTN_HELP, buttons_choice
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import logging
import psycopg2              # Для работы с PostgreSQL
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnotherVKBot:
    def __init__(self, token, db_params):
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)

        # Подключение к базе данных
        self.connection = psycopg2.connect(**db_params)
        self.cursor = self.connection.cursor()
        logger.info("Бот инициализирован и подключен к базе данных")

    # Создание клавиатуры для ответа
    def create_keyboard(self, buttons):
        keyboard = VkKeyboard(one_time=False)
        for btn_text, btn_color in buttons:
            keyboard.add_button(btn_text, color=btn_color)
        return keyboard.get_keyboard()

    # Функция отправки сообщения с кнопками
    def send_message_with_buttons(self, user_id, message, buttons):
        keyboard = VkKeyboard(one_time=True)
        for btn_text, btn_color in buttons:
            keyboard.add_button(btn_text, color=btn_color)
        self.vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            keyboard=keyboard.get_keyboard()
        )

    # Логика для поиска пары
    def find_pair(self, user_id):
        logger.info(f"Поиск пары для пользователя с ID {user_id}")
        # Пример результата поиска пары
        user_info = {
            "name": "Иван Иванов",
            "profile_link": "https://vk.com/id123456",
            "photos": ["photo123456_1", "photo123456_2", "photo123456_3"]
        }
        message = f"Имя: {user_info['name']}\nСсылка на профиль: {user_info['profile_link']}"
        attachments = ",".join(user_info['photos'])  # Пример использования VK attachment для фото
        self.send_message(user_id, message, attachment=attachments)

    # Логика для добавления пользователя в избранное
    def add_to_favorites(self, user_id, name, profile_link):
        self.cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = self.cursor.fetchone()

        if not user:
            self.cursor.execute(
                "INSERT INTO users (user_id, name, profile_link) VALUES (%s, %s, %s)",
                (user_id, name, profile_link)
            )
            self.connection.commit()
            logger.info(f"Пользователь {name} добавлен в таблицу users.")

        self.cursor.execute(
            "INSERT INTO favorites (user_id) VALUES (%s)",
            (user_id,)
        )
        self.connection.commit()
        logger.info(f"Пользователь {user_id} добавлен в избранное.")

    # Логика для показа следующего пользователя
    def show_next_user(self, user_id):
        logger.info(f"Показ следующего пользователя для {user_id}")
        user_info = {
            "name": "Мария Петрова",
            "profile_link": "https://vk.com/id654321",
            "photos": ["photo654321_1", "photo654321_2", "photo654321_3"]
        }
        message = f"Имя: {user_info['name']}\nСсылка на профиль: {user_info['profile_link']}"
        attachments = ",".join(user_info['photos'])  # Пример использования VK attachment для фото
        self.send_message(user_id, message, attachment=attachments)

    # Логика для отправки сообщения с помощью
    def send_help_message(self, user_id):
        logger.info(f"Отправка сообщения с помощью для {user_id}")
        help_text = ("Команды:\n"
                     "1. Найти пару 💓 — поиск новых людей для знакомства\n"
                     "2. Нравится 👍 — добавить человека в избранное\n"
                     "3. Следующий 👉 — показать следующего человека\n"
                     "4. Помощь 🆘 — показать это сообщение")
        self.send_message_with_buttons(user_id, help_text, buttons_choice)

    # Логика для отправки сообщения при неизвестной команде
    def send_unknown_command_message(self, user_id):
        logger.warning(f"Неизвестная команда от пользователя {user_id}")
        self.send_message_with_buttons(user_id, "Извините, я не понимаю эту команду. Используйте команду 'Помощь 🆘' для списка доступных команд.", buttons_choice)

    # Функция отправки сообщения пользователю
    def send_message(self, user_id, message, attachment=None):
        self.vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            attachment=attachment,
            keyboard=self.create_keyboard(buttons_choice)
        )

    # Обработчик сообщений
    def handle_message(self, event):
        if event.text == BTN_FIND_PAIR:
            # Запуск поиска
            self.find_pair(event.user_id)
        elif event.text == BTN_LIKE:
            # Добавление в избранное
            self.add_to_favorites(event.user_id, "Имя пользователя", "https://vk.com/id123456")  # Пример вызова с фиксированными данными
        elif event.text == BTN_NEXT:
            # Следующий пользователь
            self.show_next_user(event.user_id)
        elif event.text == BTN_HELP:
            # Помощь
            self.send_help_message(event.user_id)
        else:
            # Неизвестная команда
            self.send_unknown_command_message(event.user_id)

    # Основной цикл работы бота
    def run(self):
        logger.info("Бот запущен и готов к работе")
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.handle_message(event)

# Запуск бота
if __name__ == '__main__':
    db_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': 'localhost',
        'port': '5432'
    }
    token = os.getenv('VK_GROUP_TOKEN')  # Укажите здесь свой токен группы
    bot = AnotherVKBot(token, db_params)
    bot.run()
