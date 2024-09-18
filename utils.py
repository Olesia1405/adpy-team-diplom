"""
Будет содержать вспомогательные функци
"""
import logging
from database import Database

logger = logging.getLogger(__name__)


class DatabaseUtils(Database):
    """
    Класс для управления базой данных, наследующий методы и свойства из класса Database.
    """
    def __init__(self):
        super().__init__()

    def add_table(self):
        """
        Создание таблиц в базе данных.

        Функция создает три таблицы:
        1. Таблица пользователей (`users`) с информацией о пользователях, включая
            ID, VK ID, имя, город, возраст, пол и массив ID фотографий.

        2. Таблица кандидатов (`candidate`), с аналогичными полями как у пользователей.

        3. Таблица соответствий между пользователями и кандидатами (`user_candidate`),
            которая связывает пользователя с кандидатом через внешние ключи на таблицы
            пользователей и кандидатов, а также хранит предпочтения пользователя.

        Таблицы создаются с использованием метода `create_table`.
        """
        table_user = 'users'
        columns_user = [
            ('id', 'SERIAL PRIMARY KEY'),
            ('vk_id', 'BIGINT UNIQUE NOT NULL'),
            ('name', 'VARCHAR(255) NOT NULL'),
            ('city', 'VARCHAR(255)'),
            ('age', 'INT'),
            ('gender', 'SMALLINT CHECK (gender IN (1, 2))'),
            ('photo_ids', 'BIGINT[]')
        ]

        table_candidate = 'candidate'
        columns_candidate = columns_user

        table_user_candidate = 'user_candidate'
        columns_user_candidate = [
            ('id', 'SERIAL PRIMARY KEY'),
            ('user_id', 'BIGINT REFERENCES users(id) ON DELETE CASCADE'),
            ('candidate_id', 'BIGINT REFERENCES candidate(id) ON DELETE CASCADE'),
            ('preference', 'BOOLEAN NOT NULL')
        ]
        self.create_table(table_name=table_user, columns=columns_user)
        self.create_table(table_name=table_candidate, columns=columns_candidate)
        self.create_table(table_name=table_user_candidate, columns=columns_user_candidate)

    def check_user_existence_db(self, user_vk_id: int) -> int | None:
        """
        Проверяет, существует ли пользователь с заданным идентификатором ВКонтакте в базе данных.

            Функция выполняет запрос к базе данных для проверки наличия пользователя по его
        идентификатору ВКонтакте. Если пользователь найден, возвращается его идентификатор
        из базы данных. Если пользователь не найден, возвращается None.

        :param user_vk_id:int Уникальный идентификатор пользователя ВКонтакте.

        :return:int | None Возвращает идентификатор пользователя из базы данных, если он существует,
                или None, если пользователь не найден.
        """
        table_name = 'users'
        columns = 'vk_id'
        condition = 'vk_id=%s'
        values = (user_vk_id,)

        result = self.select_data(table_name, columns, condition, values)
        return result if result else None




