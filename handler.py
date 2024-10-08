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
from btn_text import BTN_FIND_PAIR, buttons_regist, buttons_start, \
    buttons_choice, WELCOME_MESSAGE, BTN_REGISTRATION, \
    buttons_choice_sex, BTN_SEX_MAN, BTN_LIKE, BTN_HELP, HELP_MESSAGE, BTN_DISLIKE, BTN_MAIN_MENU, BTN_CHOSEN, \
    buttons_favorites, BTN_NEXT, BTN_BACK, BTN_REMOVE_FAVORITES, buttons_favorites_next, buttons_favorites_back
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
        Атрибуты:
            - self.vk_bot: Экземпляр VKBot для взаимодействия с ВКонтакте.
            - self.send_message: Ссылка на метод vk_bot.send_message для отправки сообщений
            пользователям.
            - self.create_keyboard: Ссылка на метод vk_bot.create_keyboard для создания клавиатур.
            - self.util_db: Экземпляр класса DatabaseUtils для взаимодействия с базой данных.
            - self.utils_auxiliary: Экземпляр класса AuxiliaryUtils для вспомогательных функций.
            - self.user_data: Словарь для хранения временных данных пользователей
            (например, стадия взаимодействия).
            - self.user_candidate_data: Словарь для хранения данных о кандидатах и их статусах
            для каждого пользователя.
        """
        self.vk_bot = vk_bot
        self.send_message = vk_bot.send_message
        self.create_keyboard = vk_bot.create_keyboard
        self.util_db = DatabaseUtils()
        self.utils_auxiliary = AuxiliaryUtils()
        self.user_data = {}
        self.user_candidate_data = {}

    def message_handler(self, event, user_name: str, request: str):
        """
        Обрабатывает текстовые сообщения от пользователя и отвечает соответствующими сообщениями.

        В зависимости от текста сообщения бот отвечает пользователю приветствием,
        ищет ему пару или отправляет сообщение о том, что он не понял запрос.

        :param event: Объект события из VK API, содержащий информацию о сообщении.
        :param user_name: str Имя пользователя, которому бот отвечает.
        :param request: str Текст сообщения, отправленного пользователем.
        """

        is_user_in_db = self.util_db.check_user_existence_db(event.user_id)
        if request == "начать":
            if is_user_in_db is None:
                self.send_message(event.user_id, f"Привет, {user_name}! 👋 {WELCOME_MESSAGE}",
                                  keyboard=self.create_keyboard(buttons_regist))
            else:
                self.send_message(event.user_id, f"Привет, {user_name}! 👋",
                                  keyboard=self.create_keyboard(buttons_start))
        elif request == BTN_HELP.lower():
            self.send_message(event.user_id, HELP_MESSAGE,
                              keyboard=self.create_keyboard(buttons_start))

        elif request == BTN_REGISTRATION.lower():
            info_message = self.utils_auxiliary.prepare_user_candidate_data(event.user_id)

            self.send_message(event.user_id, f"{user_name} {info_message}",
                              keyboard=self.create_keyboard(buttons_start))

        elif request == BTN_FIND_PAIR.lower() and is_user_in_db:
            self.send_message(event.user_id, f"{user_name} кого вы ищете: "
                                             f"даму сердца или кавалера?",
                              keyboard=self.create_keyboard(buttons_choice_sex))
            self.vk_bot.set_user_state(event.user_id, "waiting_for_sex")

        elif request == 'show':
            if self.user_candidate_data[event.user_id]:
                try:
                    candidate = self.user_candidate_data[event.user_id][0]
                    massage, photo_id_list = self.utils_auxiliary.creating_kadiat_message(candidate)

                    self.send_message(event.user_id, massage,
                                      keyboard=self.create_keyboard(buttons_choice),
                                      photo_id_list=photo_id_list
                                      )
                finally:
                    self._filling_user_candidate_data_dict(self.user_data, event.user_id)

                self.vk_bot.set_user_state(event.user_id, "waiting_for_like_dislike")

            else:
                self.send_message(event.user_id, 'Город вы указали не верно. Попробуйте еще раз',
                                  keyboard=self.create_keyboard(buttons_start)
                                  )
                self.vk_bot.set_user_state(event.user_id, None)

        elif request == BTN_CHOSEN.lower():
            list_favorites = self.utils_auxiliary.get_favorites(event.user_id)

            if list_favorites is not None:

                self.user_candidate_data[event.user_id] = {'favorites': list_favorites,
                                                           'index': 0
                                                           }
                self._show_next_favorite(event, 0)

            else:
                self.send_message(event.user_id, "у вас нет избранных",
                                  keyboard=self.create_keyboard(buttons_start)
                                  )

        else:
            text = 'Я вас не понял. Активирую главное меню.'
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
        if state == "waiting_for_sex":
            if request != BTN_MAIN_MENU.lower():
                sex = 2 if request == BTN_SEX_MAN.lower() else 1
                self.user_data[user_id] = {'sex': sex}

                self.send_message(user_id,
                                  "Введите возраст или укажите диапазон возрастов, "
                                  "разделяя значения запятой.")
                self.vk_bot.set_user_state(user_id, "waiting_for_age")

            else:
                self.send_message(event.user_id, BTN_MAIN_MENU,
                                  keyboard=self.create_keyboard(buttons_start)
                                  )
                self.vk_bot.set_user_state(user_id, None)

        elif state == "waiting_for_age":
            age = request.split(',')
            self.user_data[user_id].update({'age': age})

            self.send_message(user_id,
                              "Укажите город в котором искать спутника жизни")
            self.vk_bot.set_user_state(user_id, "waiting_for_city")

        elif state == "waiting_for_city":
            self.user_data[user_id].update({'city': request})
            self._filling_user_candidate_data_dict(self.user_data, user_id)
            self.vk_bot.set_user_state(user_id, None)
            request = 'show'
            self.message_handler(event, user_name, request)

        elif state == "waiting_for_like_dislike":
            candidate_id = self.user_candidate_data[event.user_id][0]['id']

            if request == BTN_LIKE.lower():

                self.utils_auxiliary.adding_candidate_status(candidate_id, event.user_id, True)
                del self.user_candidate_data[event.user_id][0]
                self._transfer_show(event, user_name)

            elif request == BTN_DISLIKE.lower():
                self.utils_auxiliary.adding_candidate_status(candidate_id, event.user_id, False)
                del self.user_candidate_data[event.user_id][0]
                self._transfer_show(event, user_name)

            elif request == BTN_MAIN_MENU.lower():
                self.send_message(event.user_id, BTN_MAIN_MENU,
                                  keyboard=self.create_keyboard(buttons_start)
                                  )
                self.vk_bot.set_user_state(user_id, None)

            else:
                self.send_message(event.user_id, 'Не ожиданий ответ, перенаправляю в главное меню',
                                  keyboard=self.create_keyboard(buttons_start)
                                  )
                self.vk_bot.set_user_state(user_id, None)

        elif state == 'waiting_for_favorite':

            if request == BTN_NEXT.lower():
                self._show_next_favorite(event, 1)

            elif request == BTN_BACK.lower():
                self._show_next_favorite(event, -1)

            elif request == BTN_REMOVE_FAVORITES.lower():
                index = self.user_candidate_data[event.user_id]['index']
                candidate_id = self.user_candidate_data[event.user_id]['favorites'][index]['id']
                print(candidate_id)
                self.util_db.candidate_status_update(candidate_id, event.user_id, False)
                del self.user_candidate_data[event.user_id]['favorites'][index]
                self._show_next_favorite(event, 0)

            elif request == BTN_MAIN_MENU.lower():
                self.send_message(event.user_id, BTN_MAIN_MENU,
                                  keyboard=self.create_keyboard(buttons_start)
                                  )
                self.vk_bot.set_user_state(user_id, None)

            else:
                self.send_message(event.user_id, 'Не ожиданий ответ, перенаправляю в главное меню',
                                  keyboard=self.create_keyboard(buttons_start)
                                  )
                self.vk_bot.set_user_state(user_id, None)

    def _filling_user_candidate_data_dict(self, user_data: dict, user_vk_id: int):
        """
        Заполняет словарь данных кандидатов для указанного пользователя.

        Получает список кандидатов для пользователя с помощью вспомогательной функции,
        после чего сохраняет этот список в атрибуте `user_candidate_data` с ключом, соответствующим
        VK ID пользователя.

        :param user_data: Словарь с данными пользователя.
        :param user_vk_id: VK ID пользователя, для которого нужно получить список кандидатов.
        """
        candidate_list = self.utils_auxiliary.get_candidate_db(user_data, user_vk_id)
        self.user_candidate_data[user_vk_id] = candidate_list

    def _transfer_show(self, event, user_name: str):
        """
        Передает запрос на отображение кандидатов.

        Вызывает метод `message_handler` с переданным событием, именем пользователя и
        запросом на отображение списка кандидатов.

        :param event: Объект события из VK API, содержащий информацию о текущем запросе
                     пользователя.
        :param user_name: Имя пользователя, которому будет отображаться сообщение.
        """
        request = 'show'
        self.message_handler(event, user_name, request)

    def _show_next_favorite(self, event, step: int):
        """
        Отображает следующего кандидата из списка избранных для пользователя.

            Функция отвечает за вывод информации о кандидате, включая его фото и данные,
        и отправляет сообщение пользователю с клавиатурой для взаимодействия (например,
        кнопки для просмотра следующего кандидата, возврата к предыдущему или удаления
        из избранного). После отправки данных функция обновляет состояние пользователя в системе.

        :param event: объект события VK API, содержащий информацию о текущем взаимодействии
                    пользователя с ботом.

        """
        self.user_candidate_data[event.user_id]['index'] += step
        index = self.user_candidate_data[event.user_id]['index']
        favorites_list = self.user_candidate_data[event.user_id]['favorites']

        if index <= 0:
            index = 0
            keyboard = buttons_favorites_next
            self.user_candidate_data[event.user_id]['index'] = index
        elif index >= len(favorites_list):
            index = len(favorites_list) - 1
            self.user_candidate_data[event.user_id]['index'] = index
            keyboard = buttons_favorites_back
        else:
            keyboard = buttons_favorites

        candidate = favorites_list[index]
        massage, photo_id_list = self.utils_auxiliary.creating_kadiat_message(candidate)
        self.send_message(event.user_id, massage,
                          keyboard=self.create_keyboard(keyboard),
                          photo_id_list=photo_id_list
                          )
        self.vk_bot.set_user_state(event.user_id, "waiting_for_favorite")
