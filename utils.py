"""
Будет содержать вспомогательные функции
"""
import logging
import re

from datetime import datetime
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

        if common_data is not None:
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
        else:
            result = None

        if table_name == 'users':

            if result is not None:
                info_message = 'Регистрация прошла успешно✅'

            elif result is None and common_data is None:
                info_message = 'У вас закрытый профиль!.Регистрация провалена⛔'

            else:
                info_message = 'Регистрация провалена⛔'

        else:
            if common_data is not None:
                info_message = data
            else:
                info_message = None
                logger.error(f'У пользователя с вк id {user_vk_id} закрытый профиль')
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

    def get_candidate_db(self, user_data: dict, user_vk_id: int) -> list[dict]:

        """
        Получение списка кандидатов для пользователя из базы данных.

        Функция ищет кандидатов в базе данных, удовлетворяющих заданным критериям
        (возраст, пол, город). Если в базе данных недостаточно кандидатов (меньше 10),
        делает запрос к VK API для получения недостающих кандидатов и добавляет их в базу данных.
        После этого снова вызывает поиск кандидатов в базе данных и возвращает полный список.

        :param user_data: Словарь с данными пользователей, где ключ - vk_id пользователя,
                          а значение - словарь с возрастом, полом и городом.
        :param user_vk_id: VK ID пользователя, для которого необходимо найти кандидатов.

        :return: Список словарей с данными кандидатов (не менее 10).
        """
        candidate_list = []
        candidate_db = self.db_utils.search_for_candidates_db(user_data[user_vk_id]['age'],
                                                              user_data[user_vk_id]['sex'],
                                                              user_data[user_vk_id]['city'],
                                                              user_vk_id
                                                              )
        for candidate_data in candidate_db:
            age = self._calculate_age(candidate_data[4])
            data = {
                'id': candidate_data[0],
                'vk_id': candidate_data[1],
                'name': candidate_data[2],
                'city': candidate_data[3],
                'age': age,
                'gender': candidate_data[5],
                'photo_ids': candidate_data[6],
            }
            candidate_list.append(data)
        if len(candidate_list) < 10:
            self.get_candidate_vk_api(user_data, user_vk_id, 10 - len(candidate_list))
            candidate_list.extend(self.get_candidate_db(user_data, user_vk_id) or [])

        return candidate_list

    def _calculate_age(self, birthday):
        """
        Рассчитывает возраст на основе даты рождения.

        :param birthday: Дата рождения (тип datetime.date).
        :return: Возраст (количество полных лет).
        """
        today = datetime.today().date()
        return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

    def get_candidate_vk_api(self, user_data: dict, user_vk_id: int,
                             number_records: int, offset: int = 0):
        """
            Запрос кандидатов через VK API и добавление их в базу данных.

            Функция делает запрос к VK API для поиска кандидатов по возрасту, полу и городу,
        исключая тех, кто уже есть в базе данных. Если кандидатов меньше,
        чем нужно (number_records), функция вызывает себя рекурсивно с увеличенным смещением
        (offset) для получения оставшихся кандидатов.
            После получения данных, кандидаты добавляются в базу данных.

        :param user_data: Словарь с данными пользователей, где ключ - vk_id пользователя,
                          а значение - словарь с возрастом, полом и городом.
        :param user_vk_id: VK ID пользователя, для которого ищутся кандидаты.
        :param number_records: Количество недостающих записей, которые нужно получить через VK API.
        :param offset: Смещение для поиска кандидатов через VK API (по умолчанию 0).

        :return: None.
        """

        candidates_id = self.vk_service.search_users(user_data[user_vk_id]['age'],
                                                     user_data[user_vk_id]['sex'],
                                                     user_data[user_vk_id]['city'],
                                                     offset=offset
                                                     )
        candidates_missing_db = self.db_utils.find_missing_candidates(candidates_id)

        if len(candidates_missing_db) < number_records:

            for candidate_id in candidates_missing_db:
                self.prepare_user_candidate_data(candidate_id, 'candidate')

            self.get_candidate_vk_api(user_data, user_vk_id,
                                      number_records - len(candidates_missing_db),
                                      offset=offset + 1
                                      )
        else:
            for candidate_id in candidates_missing_db:
                self.prepare_user_candidate_data(candidate_id, 'candidate')

    def creating_kadiat_message(self, candidate: dict) -> tuple[str, list]:
        """
            Создает сообщение и список фотографий для кандидата.

            Функция формирует текст сообщения с информацией о кандидате
        (имя, город, возраст и ссылка на профиль ВКонтакте), а также возвращает
        список идентификаторов фотографий кандидата.

        :param candidate: dict Словарь с данными о кандидате, включая ключи:
                         'name' (имя), 'city' (город), 'age' (возраст),
                         'vk_id' (ID кандидата ВКонтакте) и 'photo_ids' (список ID фотографий).

        :return: tuple Состоит из:
                 - str: Сообщение с информацией о кандидате.
                 - list: Список идентификаторов фотографий кандидата.
        """
        message = (f"Имя: {candidate['name']}\n"
                   f"Город: {candidate['city']}\n"
                   f"Возраст: {candidate['age']}\n"
                   f"https://vk.com/id{candidate['vk_id']}"
                   )
        photo_id_list = candidate['photo_ids']
        return message, photo_id_list

    def adding_candidate_status(self, candidate_id: int, user_vk_id: int, preference: bool):
        """
        Добавляет запись в таблицу user_candidate, чтобы сохранить статус кандидата
        (например, лайк или дизлайк) для конкретного пользователя.

        :param candidate_id: Идентификатор кандидата.
        :param user_vk_id: VK ID пользователя, который оценил кандидата.
        :param preference: True для лайка, False для дизлайка.
        """

        user_id = self.db_utils.select_data('users', 'id', "vk_id = %s", (user_vk_id,))
        data = {
            'user_id': user_id[0],
            'candidate_id': candidate_id,
            'preference': preference
        }
        self.db_utils.insert_data('user_candidate', data)


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

        :return:int | None Возвращает идентификатор пользователя из базы данных,
            если он существует, или None, если пользователь не найден.
        """
        table_name = 'users'
        columns = 'vk_id'
        condition = 'vk_id=%s'
        values = (user_vk_id,)

        result = self.select_data(table_name, columns, condition, values)
        return result if result else None

    def save_user_candidate(self, data: dict, table_name: str = 'users'):
        """
        Сохраняет данные о пользователе или кандидате в указанную таблицу.

        Функция вставляет данные о пользователе или кандидате в таблицу базы данных.
        По умолчанию данные сохраняются в таблицу 'users', но можно указать другую таблицу.

        :param data: dict Словарь с данными для сохранения. Ключи словаря соответствуют названиям
                     колонок в таблице, а значения — это данные для вставки в соответствующие поля.
        :param table_name: str Название таблицы, в которую будут вставлены данные.
                           По умолчанию используется таблица 'users'.
        """
        return self.insert_data(table_name=table_name, data=data)

    def find_missing_candidates(self, vk_ids: list):
        """
        Проверка, какие кандидаты из списка vk_ids отсутствуют в таблице candidate.

        :param vk_ids: Список vk_id кандидатов для проверки.
        :return: Список vk_id кандидатов, которых нет в базе данных.
        """
        if not vk_ids:
            return []

        query = f"""
        SELECT missing.vk_id 
        FROM (VALUES {', '.join(['(%s)' for _ in vk_ids])}) AS missing(vk_id)
        LEFT JOIN candidate c ON missing.vk_id = c.vk_id
        WHERE c.vk_id IS NULL
        """
        missing_candidates = self.execute_query(query, params=tuple(vk_ids), fetch=True)

        if missing_candidates is not None:
            result = [row[0] for row in missing_candidates] if missing_candidates else []
        else:
            result = missing_candidates
        return result

    def search_for_candidates_db(self, age: list, sex: int, city: str, user_vk_id: int):
        """
            Поиск кандидатов по возрасту (конкретный или диапазон), полу и городу,
        которых пользователь еще не оценил.

        :param age: Список с двумя элементами [min_age, max_age] или одним элементом [age].
        :param sex: Пол кандидатов (1 - женский, 2 - мужской).
        :param city: Город кандидатов.
        :param user_vk_id: VK_ID пользователя, для которого ищем кандидатов.

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
        AND city ILIKE %s
        AND c.id NOT IN (
            SELECT candidate_id FROM user_candidate WHERE user_id = (
                SELECT u.id FROM users u WHERE u.vk_id = %s)
        )
        """

        values = (*age_values, sex, city, user_vk_id)

        candidates = self.select_data(table_name, columns, condition, values)
        return candidates


if __name__ == '__main__':
    r = AuxiliaryUtils()
