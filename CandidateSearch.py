"""
Инициализация:
__init__: Инициализирует объект класса с токеном и версией API.

Методы:
search_users: Выполняет поиск пользователей по городу и возрасту. Получает ID города, затем выполняет запрос users.search и собирает результаты, включая ссылки на профиль и фотографии.
get_city_id: Получает ID города по названию.
get_top_photos: Получает топ-фотографии пользователя по количеству лайков.

Использование:
Пример использования класса показан в блоке if __name__ == '__main__', где создается объект класса CandidateSearch и выполняется поиск пользователей.
Этот класс и методы позволяют интегрировать поиск пользователей и получение их фотографий в ваш VK бот.
"""

import vk_api
import logging
from vk_api.utils import get_random_id
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CandidateSearch:
    def __init__(self, token, version='5.131'):
        self.token = token
        self.version = version
        self.api_url = 'https://api.vk.com/method/'
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()

    def search_users(self, city_name, age_from, age_to, gender=1, count=10, offset=0):
        city_id = self.get_city_id(city_name)
        if city_id is None:
            logger.error(f"Не удалось найти город {city_name}.")
            return []
        
        user_token = os.getenv('VK_API_TOKEN')
        method = 'users.search'
        params = {
            'access_token': user_token,
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

        try:
            response = self.vk.users.search(**params)
            items = response.get('items', [])
            results = []

            for user in items:
                user_info = {
                    'id': user['id'],
                    'first_name': user.get('first_name', ''),
                    'last_name': user.get('last_name', ''),
                    'profile_link': f"https://vk.com/id{user['id']}",
                    'photos': self.get_top_photos(user['id'])
                }
                results.append(user_info)

            return results

        except Exception as e:
            logger.error(f"Ошибка при поиске пользователей: {e}")
            return []

    def get_city_id(self, city_name):
        user_token = os.getenv('VK_API_TOKEN')
        method = 'database.getCities'
        params = {
            'access_token': user_token,
            'v': self.version,
            'country_id': 1,  # Россия
            'q': city_name,
            'count': 1
        }
        try:
            response = self.vk.database.getCities(**params)
            items = response.get('items', [])
            if items:
                return items[0]['id']
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении ID города: {e}")
            return None

    def get_top_photos(self, user_id, top_n=4):
        method = 'photos.get'
        params = {
            'access_token': self.token,
            'v': self.version,
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        }
        try:
            response = self.vk.photos.get(**params)
            photos = response.get('items', [])
            if not photos:
                logger.warning(f"У пользователя {user_id} нет фотографий.")
                return []

            # Сортировка по количеству лайков
            sorted_photos = sorted(photos, key=lambda x: x['likes']['count'], reverse=True)
            top_photos = sorted_photos[:top_n]

            photo_urls = [photo['sizes'][-1]['url'] for photo in top_photos]  # Самый большой размер
            return photo_urls
        except Exception as e:
            logger.error(f"Ошибка при получении фотографий пользователя {user_id}: {e}")
            return []

# Пример использования класса
if __name__ == '__main__':
    token = os.getenv('VK_GROUP_TOKEN')  # Замените на свой токен
    searcher = CandidateSearch(token)

    results = searcher.search_users(city_name="Москва", age_from=25, age_to=30)
    for result in results:
        print(f"Имя: {result['first_name']} {result['last_name']}")
        print(f"Профиль: {result['profile_link']}")
        print(f"Фотографии: {', '.join(result['photos'])}")
        print()
