import psycopg2
import logging
from psycopg2 import sql
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, config_logging

# Настройка логирования

logger = logging.getLogger(__name__)


class Database:
    """
    Класс для управления подключением и операциями с базой данных.
    """

    def __init__(self, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
                 host=DB_HOST, port=DB_PORT):
        """
            Инициализация соединения с базой данных.

            :param dbname: Имя базы данных.
            :param user: Имя пользователя базы данных.
            :param password: Пароль пользователя базы данных.
            :param host: Хост базы данных (по умолчанию 'localhost').
            :param port: Порт базы данных (по умолчанию 5432).
        """
        self.conn = None
        self.cur = None
        try:
            self.conn = psycopg2.connect(dbname=dbname, user=user,
                                         password=password, host=host, port=port)
            self.cur = self.conn.cursor()
            logger.info(f"Соединение с {dbname} успешно")
        except psycopg2.OperationalError:
            logger.error(f"Ошибка подключения к {dbname}")

    def __del__(self):
        """Закрытие соединения и курсора при уничтожении объекта."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def create_table(self, table_name: str, columns: list | tuple):
        """
        Создание таблицы в базе данных.

        :param table_name: Имя таблицы.
        :param columns: Список столбцов и их типов
        в формате [('название_столбца', 'тип_данных'), ...].
        """
        try:
            self.cur.execute("""
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_name = %s
                        );
                    """, (table_name,))
            table_exists = self.cur.fetchone()[0]
            if table_exists:
                logger.info(f"Таблица {table_name} уже существует")
            else:
                columns_str = ', '.join(f'{col[0]} {col[1]}' for col in columns)
                query = sql.SQL(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})")
                self.cur.execute(query)
                self.conn.commit()
                logger.info(f"Таблица {table_name} успешно создана")
        except psycopg2.DatabaseError as e:
            logger.error(f"Ошибка при создании таблицы {table_name}: {e}")

    def drop_table(self, table_name: str):
        """
        Удаление таблицы из базы данных.

        :param table_name: Имя таблицы.
        """
        try:
            query = sql.SQL(f"DROP TABLE IF EXISTS {table_name}")
            self.cur.execute(query)
            self.conn.commit()
            logger.info(f'Таблица успешно удалена {table_name}')
        except psycopg2.DatabaseError as e:
            logger.error(f"Ошибка при удалении таблицы {table_name}: {e}")

    def insert_data(self, table_name: str, data: dict):
        """
        Вставка данных в таблицу.

        :param table_name: Имя таблицы.
        :param data: Словарь с данными для вставки
        в формате {'column1': value1, 'column2': value2, ...}.
        :return: ID вставленной записи.
        """
        try:
            columns = data.keys()
            values = list(data.values())

            for i, value in enumerate(values):
                if isinstance(value, list):
                    values[i] = '{' + ','.join(f'"{v}"' for v in value) + '}'

            query = sql.SQL(
                f"INSERT INTO {table_name} ({', '.join(columns)})"
                f" VALUES ({', '.join(['%s'] * len(values))}) RETURNING id"
            )

            self.cur.execute(query, values)
            inserted_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f'Данные {data} в таблицу {table_name} успешно добавлены')
            return inserted_id

        except psycopg2.DatabaseError as e:
            logger.error(f"Ошибка при вставке данных в таблицу {table_name}: {e}")
            return None

    def select_data(self, table_name, columns: str = '*',
                    condition: str = None, values: tuple = None):
        """
        Выполнение SELECT-запроса.

        :param table_name: Имя таблицы.
        :param columns: Список столбцов для выборки, по умолчанию '*' - все столбцы.
        :param condition: Условие WHERE для фильтрации данных, строка SQL.
        :param values: Значения для подстановки в условие WHERE, кортеж.
        :return: Список кортежей с данными.
        """
        try:
            columns_str = ', '.join(columns) if isinstance(columns, list) else columns
            query = sql.SQL(f"SELECT {columns_str} FROM {table_name}")
            if condition:
                query += sql.SQL(f" WHERE {condition}")
            self.cur.execute(query, values)
            rows = self.cur.fetchall()
            return rows
        except psycopg2.DatabaseError as e:
            logger.error(f"Ошибка при выполнении SELECT из таблицы {table_name}: {e}")
            return []

    def update_data(self, table_name: str, data: dict, condition: str, values: tuple = None):
        """
        Обновление данных в таблице.

        :param table_name: Имя таблицы.
        :param data: Словарь с данными для обновления
        в формате {'column1': value1, 'column2': value2, ...}. Если value1 это строка,
        которая содержит арифметическое выражение (например, "column + 1"),
        то она будет использована напрямую в SQL-запросе.
        :param condition: Условие WHERE для фильтрации записей, строка SQL.
        :param values: Необязательный параметр. Значения для подстановки в условие WHERE, кортеж.

        :return: True, если обновление прошло успешно, иначе False.
        """
        try:
            set_clause = []
            query_values = []

            for column, value in data.items():
                # Проверка на арифметическое выражение
                if isinstance(value, str) and any(op in value for op in ['+', '-', '*', '/']):
                    set_clause.append(f"{column} = {value}")
                else:
                    set_clause.append(f"{column} = %s")
                    query_values.append(value)

            query = sql.SQL(f"UPDATE {table_name} SET {', '.join(set_clause)} WHERE {condition}")

            if values:
                query_values.extend(values)

            self.cur.execute(query, query_values)
            self.conn.commit()
            logger.info(f'Обновление в таблице {table_name} прошло успешно')
            return True
        except psycopg2.DatabaseError as e:
            logger.error(f"Ошибка при обновлении данных в таблице {table_name}: {e}")
            return False

    def delete_data(self, table_name: str, condition: str = None, values: tuple = None) -> bool:
        """
        Выполнение DELETE-запроса.

        :param table_name: Имя таблицы, из которой нужно удалить данные.
        :param condition: Условие WHERE для фильтрации данных, строка SQL.
        :param values: Значения для подстановки в условие WHERE, кортеж.
        :return: True, если удаление прошло успешно, иначе False.
        """
        try:
            query = sql.SQL(f"DELETE FROM {table_name}")
            if condition:
                query += sql.SQL(f" WHERE {condition}")
            self.cur.execute(query, values)
            self.conn.commit()
            return True
        except psycopg2.DatabaseError as e:
            logger.error(f"Ошибка при удалении данных из таблицы {table_name}: {e}")
            self.conn.rollback()
            return False

    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """
        Выполнение произвольного SQL-запроса.

        :param query: Строка SQL-запроса.
        :param params: Параметры для вставки в запрос (опционально).
        :param fetch: Если True, будет выполнен fetchall() для получения данных.
        :return: Список кортежей с данными, если fetch=True. Иначе None.
        """
        try:
            self.cur.execute(query, params)
            self.conn.commit()
            if fetch:
                return self.cur.fetchall()
            logger.info(f'Запрос успешно выполнен: {query}')
        except psycopg2.DatabaseError as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            self.conn.rollback()
            return None


if __name__ == '__main__':
    r = Database()
    print(r.select_data('word'))


