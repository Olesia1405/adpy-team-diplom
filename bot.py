import logging
import vk_api

from database import Database
from vk_api_bot import VKAPI
from config import config_logging, VK_GROUP_TOKEN
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard
from vk_api.utils import get_random_id
from btn_text import BTN_FIND_PAIR, buttons_star, buttons_choice

# Настройка логирования
config_logging()
logger = logging.getLogger(__name__)


class VKBot:
    def __init__(self, vk_group_token):
        self.vk_bot = vk_api.VkApi(token=vk_group_token)
        self.longpoll = VkLongPoll(self.vk_bot)
        self.vk = self.vk_bot.get_api()
        logger.info("Бот успешно инициализирован")
        self.db = Database()
        self.vk_api = VKAPI()

    def create_keyboard(self, buttons: list = None, one_time: bool = True):
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

    def send_message(self, user_id: int, message: str, keyboard: object = None):
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

    def get_user_name(self, user_id:int)-> str:
        """
        Получает имя и фамилию пользователя по его user_id.
        """
        user_info = self.vk.users.get(user_ids=user_id)
        first_name = user_info[0]['first_name']
        last_name = user_info[0]['last_name']
        return f"{first_name} {last_name}"

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

                user_name = self.get_user_name(event.user_id)
                if request == "привет":
                    self.send_message(event.user_id, f"Приветствую вас! {user_name}",
                                      keyboard=self.create_keyboard(buttons_star))

                elif request == BTN_FIND_PAIR.lower():
                    self.send_message(event.user_id, f"{user_name} ищем вам пару!",
                                      keyboard=self.create_keyboard(buttons_choice))

                else:
                    self.send_message(event.user_id, "Я вас не понял. "
                                                     "Нажмите 'Найти пару' для продолжения.",
                                      keyboard=self.create_keyboard(buttons_star)
                                      )

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
