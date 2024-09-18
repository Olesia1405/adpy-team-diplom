"""
 Модуль handler.py

 Этот файл содержит класс Handler, который отвечает за обработку сообщений и
состояний пользователей в VK боте.
Основная цель модуля — реагировать на входящие текстовые сообщения и управлять
состояниями.

Структура:
- Класс Handler:
    - Инициализирует объект бота, который предоставляет функции для отправки сообщений
        и создания клавиатур.
    - messag_handler: Обрабатывает текстовые сообщения от пользователей.
    - state_handler: Управляет сообщениями, связанными с состояниями пользователей.

Пример использования:
    1. Создайте экземпляр класса Handler, передав объект VKBot:
       `handler = Handler(vk_bot)`

    2. Используйте метод `messag_handler` для обработки входящих сообщений:
       `handler.messag_handler(event, user_name, request)`

    3. Используйте метод `state_handler` для обработки текущего состояния пользователя:
       `handler.state_handler(state, event, user_id, user_name, request)`
"""
import logging
from btn_text import BTN_FIND_PAIR, buttons_regist, buttons_start, buttons_choice, welcome_message, BTN_REGISTRATION
from utils import DatabaseUtils, AuxiliaryUtils

logger = logging.getLogger(__name__)


class Handler:
    """
    Класс Handler отвечает за обработку сообщений и состояний пользователя в VK боте.

    Этот класс содержит методы для обработки текстовых сообщений от пользователей, а также
    управляет состояниями пользователей, такими как "ожидание поиска пары".

    Методы используют объект класса VKBot для отправки сообщений и создания клавиатур.
    """

    def __init__(self, vk_bot):
        """
        Инициализация объекта Handler.

        :param vk_bot: Объект класса VKBot, который предоставляет методы
                       для отправки сообщений и создания клавиатур.
        """
        self.vk_bot = vk_bot
        self.send_message = vk_bot.send_message
        self.create_keyboard = vk_bot.create_keyboard
        self.util_db = DatabaseUtils()
        self.utils_auxiliary = AuxiliaryUtils()


    def message_handler(self, event, user_name: str, request: str):
        """
        Обрабатывает текстовые сообщения от пользователя и отвечает соответствующими сообщениями.

        В зависимости от текста сообщения бот отвечает пользователю приветствием,
        ищет ему пару или отправляет сообщение о том, что он не понял запрос.

        :param event: Объект события из VK API, содержащий информацию о сообщении.
        :param user_name: str Имя пользователя, которому бот отвечает.
        :param request: str Текст сообщения, отправленного пользователем.        """

        is_user_in_db = self.util_db.check_user_existence_db(event.user_id)
        if request == "начать":
            if is_user_in_db is None:
                self.send_message(event.user_id, f"Привет, {user_name}! 👋 {welcome_message}",
                                  keyboard=self.create_keyboard(buttons_regist))
            else:
                self.send_message(event.user_id, f"Привет, {user_name}! 👋",
                                  keyboard=self.create_keyboard(buttons_start))

        elif request == BTN_REGISTRATION.lower():
            self.utils_auxiliary.prepare_user_candidate_data(event.user_id)
            self.send_message(event.user_id, f"{user_name} вы зарегистрированы!",
                              keyboard=self.create_keyboard(buttons_start))


        elif request == BTN_FIND_PAIR.lower() and is_user_in_db:
            self.send_message(event.user_id, f"{user_name} ищем вам пару!",
                              keyboard=self.create_keyboard(buttons_choice))
            self.vk_bot.set_user_state(event.user_id, "waiting_for_pair")

        else:
            text = 'Я вас не понял.Активирую главное меню.'
            if is_user_in_db is None:
                self.send_message(event.user_id, text,
                                  keyboard=self.create_keyboard(buttons_regist)
                                  )
            else:
                self.send_message(event.user_id, text,
                                  keyboard=self.create_keyboard(buttons_start)
                                  )

    def state_handler(self, state: str, event, user_id: int, user_name: str, request: str):
        """
        Обрабатывает состояние пользователя и отвечает соответствующим сообщением.

        Этот метод вызывается, когда у пользователя есть состояние, которое нужно обработать
        (например, ожидание поиска пары). Бот отвечает пользователю, что продолжает поиск,
        и сбрасывает текущее состояние.

        :param state: str Текущее состояние пользователя (например, "waiting_for_pair").
        :param event: Объект события из VK API.
        :param user_id: int Идентификатор пользователя ВКонтакте.
        :param user_name: str Имя пользователя.
        :param request: str Текст сообщения, отправленного пользователем.
        """
        if state == "waiting_for_pair":
            self.send_message(user_id, f"Вы написали: {request}. Ищем вам пару!")
            self.vk_bot.set_user_state(user_id, None)
