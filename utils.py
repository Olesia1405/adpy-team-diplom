"""
Будет содержать вспомогательные функци
"""
import logging
import re

from database import Database
from vk_api_service import VKAPI

logger = logging.getLogger(__name__)


class AuxiliaryUtils:
    """
        Класс вспомогательных утилит для работы с данными пользователя и кандидата.

        Этот класс объединяет функционал взаимодействия с VK API для получения информации
    о пользователях и кандидатах, а также работы с базой данных для сохранения полученных данных.
    Использует сервис `VKAPI` для работы с API ВКонтакте и `DatabaseUtils` для взаимодействия с
    базой данных.
    """

    def __init__(self):
        self.vk_service = VKAPI()
        self.db_utils = DatabaseUtils()

    def prepare_user_candidate_data(self, user_vk_id: int, table_name: str = 'users'):
        """
            Подготавливает данные пользователя или кандидата для сохранения в базу данных.

            Функция получает информацию о пользователе ВКонтакте, включая его имя, город,
        дату рождения, пол и фотографии, используя методы класса `VKAPI`. Затем извлекает
        идентификатор фотографии для прикрепления и формирует словарь с данными, которые
        сохраняются в таблицу базы данных.

        :param user_vk_id: int Идентификатор пользователя ВКонтакте.
        :param table_name: str Название таблицы базы данных для сохранения данных
            (по умолчанию 'users').
        """
        common_data = self.vk_service.get_users_info(user_vk_id)
        photo_url = self.vk_service.get_top_photos(user_vk_id)
        photo_id = self._extract_photo_attachment(photo_url) if photo_url else None
        name = f"{common_data['first_name'] if common_data['first_name'] != 'None' else ''}" \
               f" {common_data['last_name'] if common_data['last_name'] != 'None' else ''}"
        data = {
            'vk_id': common_data['id'],
            'name': name,
            'city': common_data['city'],
            'birthday': common_data['bdate'],
            'gender': common_data['sex'],
            'photo_ids': photo_id,
        }
        result = self.db_utils.insert_data(table_name, data)

        if result is not None:
            info_message = 'Регистрация прошла успешно✅'
        else:
            info_message = 'Регистрация провалена⛔'
        return info_message

    def _extract_photo_attachment(self, photo_url_list: list[str]) -> list[str] | None:
        """
        Извлечение идентификаторов фотографий из списка URL-адресов.

        Эта функция принимает список URL-адресов фотографий и извлекает
        идентификаторы фотографий в формате 'photo{owner_id}_{photo_id}'.
        Если хотя бы один URL не соответствует ожидаемому формату,
        функция вернет None. В противном случае вернется строка,
        содержащая идентификаторы, разделенные запятыми.

        :param photo_url_list: list[str]
                Список URL-адресов фотографий, из которых необходимо
                извлечь идентификаторы.

        :return: list[str] Строка с идентификаторами фотографий, разделенными запятыми,
            или None, если ни один из URL не соответствует формату.
        """

        result = []
        for photo_url in photo_url_list:
            match = re.search(r'photo(\d+_\d+)', photo_url)

            if match:
                result.append(match.group(0))
            else:
                result = None

        return result

    def test(self, user_data: dict, user_vk_id: int):

        response = self.vk_service.search_users(user_data[user_vk_id]['age'],
                                                user_data[user_vk_id]['sex'],
                                                user_data[user_vk_id]['city'],

                                                )
        print(response)


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
            ('birthday', 'DATE'),
            ('gender', 'SMALLINT CHECK (gender IN (1, 2))'),
            ('photo_ids', 'TEXT[]')
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

    def seve_user_candidate(self, data: dict, table_name: str = 'users'):
        return self.insert_data(table_name=table_name, data=data)

    def search_for_candidates_db(self, age: list, sex: int, city: str, user_id: int):
        """
            Поиск кандидатов по возрасту (конкретный или диапазон), полу и городу,
        которых пользователь еще не оценил.

        :param age: Список с двумя элементами [min_age, max_age] или одним элементом [age].
        :param sex: Пол кандидатов (1 - женский, 2 - мужской).
        :param city: Город кандидатов.
        :param user_id: ID пользователя, для которого ищем кандидатов.

        :return: Список кандидатов, которые соответствуют критериям.
        """

        if len(age) == 1:

            age_condition = "DATE_PART('year', AGE(CURRENT_DATE, birthday)) = %s"
            age_values = (age[0],)
        else:
            age_condition = "DATE_PART('year', AGE(CURRENT_DATE, birthday)) BETWEEN %s AND %s"
            age_values = (age[0], age[1])

        table_name = 'candidate c'
        columns = '*'
        condition = f"""
        {age_condition}
        AND gender = %s
        AND city = %s
        AND c.id NOT IN (
            SELECT candidate_id FROM user_candidate WHERE user_id = %s
        )
        """

        values = (*age_values, sex, city, user_id)

        candidates = self.select_data(table_name, columns, condition, values)
        return candidates


if __name__ == '__main__':
    r = AuxiliaryUtils()
