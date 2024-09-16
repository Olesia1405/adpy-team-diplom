from config import VK_API_TOKEN, VK_API_VERSION
import logging
import requests

# Настройка логирования

logger = logging.getLogger(__name__)


class VKAPI:
    def __init__(self):
        self.token = VK_API_TOKEN
        self.version = VK_API_VERSION
        self.api_url = 'https://api.vk.com/method/'

    def _error_api(self, response):
        """
        Обрабатывает ошибки ответа API
        :param response: ответ от сервера
        :return: str кодом ошибки
        """
        if list(response.json().keys())[0] != 'response':
            if response.json()['error']['error_code'] == 5:
                output_ = "Ошибка авторизации ваш токен не действителен"
            else:
                output_ = f"Произошла ошибка  код ошибки " \
                          f"{response.json()['error']['error_code']}." \
                          f"\nСмотрите в домунтациик VK API\nhttps://dev.vk.com/ru/reference/errors"
        else:
            output_ = 'Пользователя не найден'

        logger.error(output_)

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
            'fields': 'sex, bdate'
        }
        response = requests.get(self.api_url + 'users.get',
                                params=params, timeout=0.5)
        if 'error' not in response.json().keys() and response.json()['response'] != []:
            response_dict = response.json()['response'][0]
            output_ = {
                'first_name': response_dict['first_name'],
                'last_name': response_dict['last_name'],
                'sex': response_dict['sex'],
                'bdate': response_dict['bdate']
            }

        else:
            output_ = None
            self._error_api(response)

        return output_

    def get_city_id(self, city_name):
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
            logger.error(f"HTTP ошибка VK API: {response.status_code}")
            return None

    def search_users(self, age, gender, city_name, count=10, offset=0):
        # Получаем идентификатор города перед поиском
        city_id = self.get_city_id(city_name)
        if city_id is None:
            logger.error(f"Не удалось получить идентификатор города для {city_name}")
            return []

        method = 'users.search'
        params = {
            'access_token': self.token,
            'v': self.version,
            'age_from': age,
            'age_to': age,
            'sex': gender,
            'city': city_id,
            'has_photo': 1,
            'count': count,
            'offset': offset,
            'fields': 'photo_max'
        }
        response = requests.get(self.api_url + method, params=params)
        if response.status_code == 200:
            data = response.json()
            # Проверка на ошибку авторизации
            if 'error' in data and data['error']['error_code'] == 5:
                logger.error(f"Ошибка авторизации пользователя: {data['error']['error_msg']}")
                raise Exception("Ошибка авторизации пользователя: неверный токен")

            if 'response' in data:
                return data['response']['items']

            else:
                logger.error(f"Ошибка в ответе VK API: {data}")
                return []
        else:
            logger.error(f"HTTP ошибка VK API: {response.status_code}")
            return []

    def get_top_photos(self, user_id, top_n=3):
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

            # Проверка на ошибку авторизации
            if 'error' in data and data['error']['error_code'] == 5:
                logger.error(f"Ошибка авторизации пользователя: {data['error']['error_msg']}")
                raise Exception("Ошибка авторизации пользователя: неверный токен")

            if 'response' in data:
                photos = data['response']['items']

                # Если у пользователя нет фотографий
                if not photos:
                    logger.warning(f"У пользователя {user_id} нет фотографий.")
                    return []

                # Сортируем фотографии по количеству лайков
                sorted_photos = sorted(photos, key=lambda x: x['likes']['count'], reverse=True)
                top_photos = sorted_photos[:top_n]
                photo_urls = [photo['sizes'][-1]['url'] for photo in top_photos]  # Берем самый большой размер
                return photo_urls

            else:
                logger.error(f"Ошибка в ответе VK API: {data}")
                return []

        else:
            logger.error(f"HTTP ошибка VK API: {response.status_code}")
            return []


if __name__ == '__main__':
    r = VKAPI()
    print(r.get_users_info('diann_sss'))
