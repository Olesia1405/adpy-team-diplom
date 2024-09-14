"""
    Модуль bot.py

    Этот модуль реализует VK бота с использованием VK API и Long Polling для обработки сообщений
от пользователей.
    Он включает функционал для отправки сообщений, создания клавиатур, управления состояниями
    пользователей и обработки событий.

Структура:
- Класс VKBot:
    - Инициализирует подключение к VK API и базовым функционалом бота.
    - Предоставляет методы для отправки сообщений, создания клавиатур и управления состояниями
        пользователей.
    - Метод run запускает основной цикл прослушивания событий от пользователей.

Пример использования:
    1. Создайте экземпляр класса VKBot:
       `bot = VKBot(vk_group_token)`

    2. Используйте метод `run` для запуска бота:
       `bot.run()`
"""
import logging
import vk_api

from database import Database
from vk_api_bot import VKAPI
from config import config_logging, VK_GROUP_TOKEN
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard
from vk_api.utils import get_random_id
from handler import Handler

# Настройка логирования
config_logging()
logger = logging.getLogger(__name__)


class VKBot:
    """
        Класс VKBot.

        Этот класс представляет VK бота, который использует VK API и Long Polling для взаимодействия
    с пользователями.
        Он предоставляет методы для отправки сообщений, создания клавиатур и управления состояниями
    пользователей.

    Атрибуты:
    - vk_bot: Экземпляр VkApi для взаимодействия с VK API.
    - longpoll: Экземпляр VkLongPoll для получения событий.
    - vk: Объект API для работы с VK методами.
    - db: Экземпляр базы данных для взаимодействия с хранилищем данных.
    - vk_api: Дополнительный объект API.
    - handler: Объект класса Handler для обработки сообщений и состояний пользователей.
    - user_states: Словарь для хранения состояний пользователей.
    """

    def __init__(self, vk_group_token: str):
        """
        Инициализирует экземпляр VKBot.

        :param vk_group_token: str Токен группы ВКонтакте для доступа к API.
        """
        self.vk_bot = vk_api.VkApi(token=vk_group_token)
        self.longpoll = VkLongPoll(self.vk_bot)
        self.vk = self.vk_bot.get_api()

        self.db = Database()
        self.vk_api = VKAPI()
        self.handler = Handler(self)
        self.user_states = {}
        logger.info("Бот успешно инициализирован")

    def create_keyboard(self, buttons: list[tuple[str, str]] = None,
                        one_time: bool = True) -> VkKeyboard:
        """
        Создание универсальной клавиатуры с возможностью добавления произвольных кнопок.

        :param buttons: Список кнопок в формате [(название, цвет)], где цвет - это VkKeyboardColor.
        :param one_time: Если True, клавиатура будет исчезать после использования.
        :return: Экземпляр клавиатуры.
        """
        keyboard = VkKeyboard(one_time=one_time)

        for name, color in buttons:
            keyboard.add_button(name, color=color)

        return keyboard

    def send_message(self, user_id: int, message: str, keyboard: VkKeyboard = None):
        """
        Отправка сообщения пользователю с опциональной клавиатурой.

        Эта функция использует метод `messages.send` из API ВКонтакте для отправки текстового
        сообщения указанному пользователю. При необходимости можно добавить клавиатуру, которая
        будет отображаться вместе с сообщением.

        :param user_id: int Уникальный идентификатор пользователя ВКонтакте,
                            которому будет отправлено сообщение.

        :param keyboard: str Текст сообщения, которое будет отправлено пользователю.
                             Не должно быть пустым.

        :param message: object Объект клавиатуры, который будет отправлен вместе с сообщением.
                        Если значение не указано, клавиатура не будет добавлена. Ожидается,
                        что объект клавиатуры имеет метод `get_keyboard()`, который возвращает
                        клавиатуру в формате, необходимом для отправки через API.
        """

        self.vk.messages.send(
            user_id=user_id,
            message=message,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard() if keyboard else None
        )
        logger.info(f"Отправлено сообщение пользователю {user_id}: {message}")

    def get_user_name(self, user_id: int) -> str:
        """
        Получает имя и фамилию пользователя по его user_id.

        :param user_id: int Уникальный идентификатор пользователя ВКонтакте.
        :return: str Имя и фамилия пользователя в формате 'Имя Фамилия'.
        """
        user_info = self.vk.users.get(user_ids=user_id)
        first_name = user_info[0]['first_name']
        last_name = user_info[0]['last_name']
        return f"{first_name} {last_name}"

    def set_user_state(self, user_id: int, state: str):
        """
        Устанавливает состояние для пользователя.

        :param user_id: int Уникальный идентификатор пользователя ВКонтакте.
        :param state: str Новое состояние пользователя.
        """
        self.user_states[user_id] = state

    def get_user_state(self, user_id: int) -> str:
        """
        Получает текущее состояние пользователя.

        :param user_id: int Уникальный идентификатор пользователя ВКонтакте.
        :return: str Текущее состояние пользователя или None, если состояние не установлено.
        """
        return self.user_states.get(user_id)

    def run(self):
        """
        Основной цикл прослушивания событий.

        Эта функция запускает основной цикл, который прослушивает события от пользователей
        ВКонтакте через Long Poll API. При получении нового сообщения от пользователя
        функция обрабатывает текст сообщения и отправляет соответствующий ответ.
        """
        logger.info("Бот начал прослушивание событий...")

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.lower()
                user_id = event.user_id
                user_name = self.get_user_name(user_id)
                state = self.get_user_state(user_id)

                if state:
                    self.handler.state_handler(state, event, user_id, user_name, request)
                else:
                    self.handler.message_handler(event, user_name, request)

    def find_and_save_users(self, age, gender, city):
        users = self.vk_api.search_users(age, gender, city)
        for user in users:
            vk_id = user['id']
            first_name = user.get('first_name', '')
            last_name = user.get('last_name', '')
            name = f"{first_name} {last_name}".strip()
            city_name = user['city']['title'] if 'city' in user and user['city'] else None
            user_age = user.get('age', None)
            user_gender = user.get('sex', None)  # 1 — женский, 2 — мужской
            gender_char = 'F' if user_gender == 1 else 'M' if user_gender == 2 else None

            user_id = self.db.insert_user(vk_id, name, city_name, user_age, gender_char)
            if user_id:
                # Получение и сохранение фотографий
                photos = self.vk_api.get_top_photos(vk_id)
                for photo_url in photos:
                    # Для простоты считаем количество лайков равным нулю
                    # Вы можете расширить метод get_top_photos, чтобы возвращать также количество лайков
                    self.db.insert_photo(user_id, photo_url, likes_count=0)

    def add_favorite_user(self, user_id, favorite_vk_id):
        self.db.add_favorite(user_id, favorite_vk_id)

    def list_favorites(self, user_id):
        favorites = self.db.get_favorites(user_id)
        for fav in favorites:
            vk_id, date_added = fav
            print(f"VK ID: {vk_id}, Дата добавления: {date_added}")

    def close(self):
        self.db.close()


# Пример использования
if __name__ == '__main__':
    bot = VKBot(VK_GROUP_TOKEN)
    bot.run()

    # try:
    #     # Пример поиска и сохранения пользователей
    #     age = 25
    #     gender = 1  # 1 — женский, 2 — мужской
    #     city = 'Москва'
    #     bot.find_and_save_users(age, gender, city)
    #
    #     # Пример добавления в избранные
    #     user_id = 1  # ID пользователя в нашей системе
    #     favorite_vk_id = 123456789
    #     bot.add_favorite_user(user_id, favorite_vk_id)
    #
    #     # Пример вывода избранных
    #     bot.list_favorites(user_id)
    # finally:
    #     bot.close()
