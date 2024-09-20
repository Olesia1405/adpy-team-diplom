"""
Модуль для взаимодействия с VK API.

Этот модуль предоставляет класс `VKAPI`, который позволяет выполнять различные запросы к VK API,
включая получение информации о пользователях, поиск пользователей по заданным критериям,
а также получение топовых фотографий пользователя по количеству лайков.

Основные возможности:
- Получение информации о пользователе ВКонтакте.
- Поиск пользователей по возрасту, полу и городу.
- Получение топ-N фотографий пользователя.
- Обработка ошибок VK API с логированием.

Для работы с VK API требуется токен доступа, который передается при инициализации класса.
"""
import logging
import requests
import re
from config import VK_API_TOKEN, VK_API_VERSION

# Настройка логирования

logger = logging.getLogger(__name__)


class VKAPI:
    """
    Класс для взаимодействия с VK API.

        Этот класс предоставляет методы для выполнения запросов к VK API, включая получение
    информации о пользователях, поиск пользователей и получение фотографий. В случае ошибок
    взаимодействия с API используются встроенные механизмы логирования для записи ошибок.

    Атрибуты:
    ----------
    - token : str
        Токен доступа к VK API, используемый для авторизации запросов.
    - version : str
        Версия API, которая используется для запросов.
    - api_url : str
        Базовый URL для выполнения запросов к VK API.

    Методы:
    -------
    - _error_api(response):
        Обрабатывает ошибки ответа VK API и логирует их.

    - get_users_info(user_id: int | str) -> dict | None:
        Получает информацию о пользователе ВКонтакте по его идентификатору.

    - _format_bdate(date: str) -> str | None:
        Форматирует дату рождения из формата 'дд.мм.гггг' в формат 'гггг-мм-дд'.

    - _get_city_id(city_name: str) -> int | None:
        Получает идентификатор города по его названию.

    - search_users(age: list[int], gender: int, city_name: str, count: int = 10,
    offset: int = 0) -> list | int: Ищет пользователей ВКонтакте по возрасту, полу и городу.

    - get_top_photos(user_id, top_n=3) -> list:
        Получает топ-N фотографий пользователя ВКонтакте по количеству лайков.
    """

    def __init__(self):
        self.token = VK_API_TOKEN
        self.version = VK_API_VERSION
        self.api_url = 'https://api.vk.com/method/'

    def _error_api(self, response):
        """
        Обрабатывает ошибки ответа API и логирует их.

        :param response: Ответ от сервера VK API.
        :return: None
        """
        try:
            logger.error(f"Ошибка в ответе от VK API. HTTP статус: {response.status_code}")

            response_json = response.json()
            logger.debug(f"Ответ от VK API: {response_json}")

            if 'error' in response_json:
                error_code = response_json['error']['error_code']
                if error_code == 5:
                    output_ = "Ошибка авторизации: ваш токен не действителен."
                    logger.error("Ошибка авторизации (код 5). Токен устарел или недействителен.")
                else:
                    output_ = (f"Произошла ошибка. Код ошибки: {error_code}. "
                               f"Смотрите в документации VK "
                               f"API: https://dev.vk.com/ru/reference/errors")
                    logger.error(f"Ошибка VK API (код {error_code}).")
            else:
                output_ = 'Пользователь не найден'
                logger.error("Пользователь не найден в ответе VK API.")

            logger.error(f"Сообщение об ошибке: {output_}")

        except Exception as e:
            logger.exception(f"Ошибка при обработке ответа от VK API: {e}")

    def get_users_info(self, user_id: int | str) -> dict | None:
        """
        Получает информацию о пользователе ВКонтакте, включая имя, фамилию, пол и дату рождения.

        Функция отправляет запрос к API ВКонтакте для получения данных о пользователе по его ID.
        Возвращает словарь с ключами 'first_name', 'last_name', 'sex' и 'bdate', если запрос
        успешен, либо вызывает метод `_error_api` при ошибке.

        :param user_id: int Уникальный идентификатор пользователя ВКонтакте.

        :return: dict Словарь с данными о пользователе:
            - 'first_name' (str): Имя пользователя.
            - 'last_name' (str): Фамилия пользователя.
            - 'sex' (int): Пол пользователя (1 - женский, 2 - мужской, 0 - не указан).
            - 'bdate' (str): Дата рождения пользователя в формате 'дд.мм.гггг' или 'дд.мм'.

        :raises: Исключения не выбрасываются, но при наличии ошибки вызывается
                 функция `_error_api`.
        """
        params = {
            'access_token': self.token,
            'v': self.version,
            'user_ids': user_id,
            'fields': 'sex, bdate, city'
        }
        response = requests.get(self.api_url + 'users.get',
                                params=params, timeout=0.5)
        if 'error' not in response.json().keys() and response.json()['response'] != []:
            response_dict = response.json()['response'][0]
            bdate = self._format_bdate(response_dict.get('bdate', None))

            result = {
                'id': response_dict.get('id'),
                'first_name': response_dict.get('first_name', None),
                'last_name': response_dict.get('last_name', None),
                'city': response_dict.get('city', {}).get('title', None),
                'sex': response_dict.get('sex', None),
                'bdate': bdate
            }

        else:
            result = None
            self._error_api(response)

        return result

    def _format_bdate(self, date: str) -> str | None:
        """
        Форматирует дату рождения из формата 'дд.мм.гггг' в формат 'гггг-мм-дд'.

        :param date: str Дата рождения в формате 'дд.мм.гггг'.

        :return: str Дата рождения в формате 'гггг-мм-дд' или None,
            если дата неполная или неверная.
        """
        if date and re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', date):
            day, month, year = date.split('.')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        return None

    def _get_city_id(self, city_name: str) -> int | None:
        """
        Получение идентификатора города по его названию.

        Функция делает запрос к VK API для получения списка городов с указанным
        именем и возвращает идентификатор первого найденного города.

        :param city_name: str Название города, для которого нужно получить ID.

        :return: int Идентификатор города, если запрос успешен, иначе None.
        """
        method = 'database.getCities'
        params = {
            'access_token': self.token,
            'v': self.version,
            'country_id': 1,  # Russia ID
            'q': city_name,
            'count': 1
        }
        response = requests.get(self.api_url + method, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and data['response']['items']:
                return data['response']['items'][0]['id']
            else:
                logger.error(f"Ошибка в ответе VK API: {data}")
                return None
        else:
            self._error_api(response)
            return None

    def search_users(self, age: list[int], gender: int, city_name: str,
                     count: int = 10, offset: int = 0) -> list | int:
        """
        Поиск пользователей ВКонтакте по возрасту, полу и городу.

        Функция делает запрос к VK API для поиска пользователей по заданным
        параметрам (возраст, пол, город) и возвращает список их идентификаторов.

        :param age: list[int] Список с возрастом или диапазоном возрастов для поиска.
                    Например, [25] для поиска 25-летних или [25, 30] для поиска пользователей
                    в возрасте от 25 до 30 лет.
        :param gender: int Пол пользователя (1 - женский, 2 - мужской).
        :param city_name: str Название города для поиска пользователей.
        :param count: int Количество возвращаемых результатов (по умолчанию 10).
        :param offset: int Смещение для постраничного вывода (по умолчанию 0).

        :return: list[int] Список идентификаторов найденных пользователей, если запрос успешен,
            иначе None.
        """
        city_id = self._get_city_id(city_name)
        if city_id is None:
            logger.error(f"Не удалось получить идентификатор города для {city_name}")
            return []

        if len(age) > 1:
            age_from = age[0]
            age_to = age[1]
        else:
            age_from = age[0]
            age_to = age_from

        method = 'users.search'
        params = {
            'access_token': self.token,
            'v': self.version,
            'age_from': age_from,
            'age_to': age_to,
            'sex': gender,
            'city': city_id,
            'has_photo': 1,
            'count': count,
            'offset': offset,
            'fields': 'photo_max'
        }
        result = []
        response = requests.get(self.api_url + method, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                for vk_id in data['response']['items']:
                    result.append(vk_id['id'])

            else:
                self._error_api(response)
                result = None
        else:
            self._error_api(response)
            result = None
        return result

    def get_top_photos(self, user_id, top_n=3):
        """
            Получение топ-N фотографий пользователя из альбома профиля ВКонтакте, отсортированных
        по количеству лайков.

            Функция делает запрос к VK API для получения фотографий пользователя из альбома
        "profile", сортирует их по количеству лайков и возвращает ссылки на N лучших фотографий.

        :param user_id: int Идентификатор пользователя ВКонтакте, чьи фотографии будут запрошены.
        :param top_n: int Количество лучших фотографий, которые нужно вернуть (по умолчанию 3).

        :return: list Список URL-адресов топ-N фотографий пользователя. Если фотографий нет или
            произошла ошибка, возвращается пустой список.
        :raises: Exception В случае ошибки авторизации (неверный токен).
        """

        method = 'photos.get'
        params = {
            'access_token': self.token,
            'v': self.version,
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 0
        }
        response = requests.get(self.api_url + method, params=params)
        if response.status_code == 200:
            data = response.json()

            if 'error' in data and data['error']['error_code'] == 5:
                logger.error(f"Ошибка авторизации пользователя: {data['error']['error_msg']}")
                raise Exception("Ошибка авторизации пользователя: неверный токен")

            if 'response' in data:
                photos = data['response']['items']

                if not photos:
                    logger.warning(f"У пользователя {user_id} нет фотографий.")
                    return None

                sorted_photos = sorted(photos, key=lambda x: x['likes']['count'], reverse=True)
                top_photos = sorted_photos[:top_n]

                photo_urls = [
                    f"https://vk.com/{user_id}?z=photo{photo['owner_id']}_{photo['id']}" \
                    f"/photo_feed{photo['owner_id']}"
                    for photo in top_photos
                ]
                return photo_urls

            else:
                logger.error(f"Ошибка в ответе VK API: {data}")
                return None

        else:
            self._error_api(response)
            return None


if __name__ == '__main__':
    from my_test import id_test1, id_test2, id_test3, id_test4

    r = VKAPI()
    print(r.get_users_info(id_test1))
    print(r.get_users_info(id_test2))
    print(r.get_users_info(id_test3))
    print(r.get_users_info(id_test4))
    print(r.get_top_photos(id_test4))
