from database import Database
from vk_api_bot import VKAPI
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VKBot:
    def __init__(self):
        self.db = Database()
        self.vk = VKAPI()

    def find_and_save_users(self, age, gender, city):
        users = self.vk.search_users(age, gender, city)
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
                photos = self.vk.get_top_photos(vk_id)
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
    bot = VKBot()
    try:
        # Пример поиска и сохранения пользователей
        age = 25
        gender = 1  # 1 — женский, 2 — мужской
        city = 'Москва'
        bot.find_and_save_users(age, gender, city)

        # Пример добавления в избранные
        user_id = 1  # ID пользователя в нашей системе
        favorite_vk_id = 123456789
        bot.add_favorite_user(user_id, favorite_vk_id)

        # Пример вывода избранных
        bot.list_favorites(user_id)
    finally:
        bot.close()
