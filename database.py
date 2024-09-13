import psycopg2
# from psycopg2 import sql
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
import logging

# Настройка логирования

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            self.cur = self.conn.cursor()
            logger.info("Подключение к базе данных успешно.")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def insert_user(self, vk_id, name, city, age, gender):
        try:
            query = """
                INSERT INTO users (vk_id, name, city, age, gender)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (vk_id) DO NOTHING
                RETURNING id;
            """
            self.cur.execute(query, (vk_id, name, city, age, gender))
            result = self.cur.fetchone()
            self.conn.commit()
            if result:
                user_id = result[0]
                logger.info(f"Новый пользователь добавлен с ID: {user_id}")
                return user_id
            else:
                logger.info(f"Пользователь с VK ID {vk_id} уже существует.")
                return None
        except Exception as e:
            logger.error(f"Ошибка вставки пользователя: {e}")
            self.conn.rollback()
            return None

    def insert_photo(self, user_id, photo_url, likes_count):
        try:
            query = """
                INSERT INTO photos (user_id, photo_url, likes_count)
                VALUES (%s, %s, %s)
                RETURNING id;
            """
            self.cur.execute(query, (user_id, photo_url, likes_count))
            photo_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Фотография добавлена с ID: {photo_id}")
            return photo_id
        except Exception as e:
            logger.error(f"Ошибка вставки фотографии: {e}")
            self.conn.rollback()
            return None

    def add_favorite(self, user_id, favorite_vk_id):
        try:
            query = """
                INSERT INTO favorites (user_id, favorite_vk_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id;
            """
            self.cur.execute(query, (user_id, favorite_vk_id))
            result = self.cur.fetchone()
            self.conn.commit()
            if result:
                favorite_id = result[0]
                logger.info(f"Избранный пользователь добавлен с ID: {favorite_id}")
                return favorite_id
            else:
                logger.info(f"Избранный пользователь с VK ID {favorite_vk_id} уже добавлен.")
                return None
        except Exception as e:
            logger.error(f"Ошибка добавления избранного: {e}")
            self.conn.rollback()
            return None

    def get_favorites(self, user_id):
        try:
            query = """
                SELECT favorite_vk_id, date_added
                FROM favorites
                WHERE user_id = %s
                ORDER BY date_added DESC;
            """
            self.cur.execute(query, (user_id,))
            favorites = self.cur.fetchall()
            return favorites
        except Exception as e:
            logger.error(f"Ошибка получения избранных: {e}")
            return []

    def close(self):
        self.cur.close()
        self.conn.close()
        logger.info("Соединение с базой данных закрыто.")
