import requests
from config import VK_TOKEN, VK_API_VERSION
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VKAPI:
    def __init__(self):
        self.token = VK_TOKEN
        self.version = VK_API_VERSION
        self.api_url = 'https://api.vk.com/method/'

    def search_users(self, age, gender, city, count=10, offset=0):
        method = 'users.search'
        params = {
            'access_token': self.token,
            'v': self.version,
            'age_from': age,
            'age_to': age,
            'sex': gender,
            'city': city,
            'has_photo': 1,
            'count': count,
            'offset': offset,
            'fields': 'photo_max'
        }
        response = requests.get(self.api_url + method, params=params)
        if response.status_code == 200:
            data = response.json()
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
            if 'response' in data:
                photos = data['response']['items']
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
