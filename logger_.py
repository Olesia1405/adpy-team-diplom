import logging
import psycopg2
import requests
import os
from dotenv import load_dotenv

# Настройка логгера
logging.basicConfig(
    filename='vk_bot.log',  # Имя файла для логов
    level=logging.INFO,  # Уровень логгирования (INFO, ERROR и т.д.)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат логов
)

# Пример подключения к базе данных
def get_db_connection():
    load_dotenv()
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST')
        )
        logging.info("Подключение к базе данных установлено.")
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        raise

# Функция для добавления пользователя
def insert_user(vk_id, name, city, age, gender):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        INSERT INTO users (vk_id, name, city, age, gender)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (vk_id) DO NOTHING
        RETURNING id;
        """
        cur.execute(query, (vk_id, name, city, age, gender))
        user_id = cur.fetchone()
        conn.commit()
        if user_id:
            logging.info(f"Пользователь {name} (ID: {vk_id}) успешно добавлен в БД.")
        return user_id
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя {name}: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# Функция для добавления фотографии
def insert_photo(user_id, photo_url, likes_count):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        INSERT INTO photos (user_id, photo_url, likes_count)
        VALUES (%s, %s, %s)
        """
        cur.execute(query, (user_id, photo_url, likes_count))
        conn.commit()
        logging.info(f"Фото для пользователя с ID {user_id} успешно добавлено.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении фото для пользователя {user_id}: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# Функция для добавления в избранные
def add_to_favorites(user_id, favorite_vk_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        INSERT INTO favorites (user_id, favorite_vk_id)
        VALUES (%s, %s)
        ON CONFLICT (user_id, favorite_vk_id) DO NOTHING;
        """
        cur.execute(query, (user_id, favorite_vk_id))
        conn.commit()
        logging.info(f"Пользователь с ID {favorite_vk_id} добавлен в избранные для пользователя {user_id}.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя с ID {favorite_vk_id} в избранные: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# Функция для получения списка избранных
def get_favorites(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        SELECT u.name, u.vk_id 
        FROM favorites f
        JOIN users u ON f.favorite_vk_id = u.vk_id
        WHERE f.user_id = %s;
        """
        cur.execute(query, (user_id,))
        favorites = cur.fetchall()
        logging.info(f"Получен список избранных для пользователя с ID {user_id}.")
        return favorites
    except Exception as e:
        logging.error(f"Ошибка при получении списка избранных для пользователя {user_id}: {e}")
    finally:
        cur.close()
        conn.close()
