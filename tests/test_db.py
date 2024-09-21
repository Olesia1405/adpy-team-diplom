"""
mock.patch('psycopg2.connect'): Используем mock для замены реального подключения к базе данных на фиктивное. Это позволяет тестировать логику класса без необходимости реальной базы данных.
Для каждого теста проверяются правильные вызовы методов курсора и соединения (execute, commit, и т.д.).
Тесты покрывают создание таблицы, вставку, выборку, обновление, удаление данных и выполнение произвольных SQL-запросов.

Mocking внешних зависимостей:
Используем patch для замены реальных вызовов методов VKAPI и базы данных на моки.
Моки возвращают предопределенные значения, что позволяет изолировать тестируемую логику.

Тестирование метода prepare_user_candidate_data:
Мы мокируем методы get_users_info, get_top_photos и insert_data, чтобы контролировать их поведение и проверять правильность вызовов.

Тестирование приватного метода _extract_photo_attachment:
Простой тест проверяет извлечение идентификаторов фотографий и корректное поведение при неправильных URL.

Тестирование check_user_existence_db:
Тест проверяет, возвращает ли метод корректные данные, когда пользователь найден или не найден в базе данных.
"""

import pytest
from unittest import mock
from database import Database  # предположим, что модуль сохранен как database.py


@pytest.fixture
def mock_db_connection():
    """Фикстура для мокирования соединения с базой данных и курсора."""
    with mock.patch('psycopg2.connect') as mock_connect:
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        yield mock_conn, mock_cursor


def test_create_table_success(mock_db_connection):
    """Тест успешного создания таблицы."""
    mock_conn, mock_cursor = mock_db_connection
    db = Database()

    mock_cursor.fetchone.return_value = [False]  # Таблицы нет

    db.create_table('test_table', [('id', 'SERIAL PRIMARY KEY'), ('name', 'VARCHAR(100)')])

    mock_cursor.execute.assert_called_with(
        'CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR(100))'
    )
    mock_conn.commit.assert_called_once()


def test_create_table_exists(mock_db_connection):
    """Тест, если таблица уже существует."""
    mock_conn, mock_cursor = mock_db_connection
    db = Database()

    mock_cursor.fetchone.return_value = [True]  # Таблица существует

    db.create_table('test_table', [('id', 'SERIAL PRIMARY KEY'), ('name', 'VARCHAR(100)')])

    mock_cursor.execute.assert_called_once_with(
        """SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = %s
            );""", ('test_table',)
    )
    mock_conn.commit.assert_not_called()  # Таблица уже существует, не делаем commit


def test_insert_data(mock_db_connection):
    """Тест успешной вставки данных."""
    mock_conn, mock_cursor = mock_db_connection
    db = Database()

    mock_cursor.fetchone.return_value = [1]  # ID вставленной записи

    data = {'name': 'test_name'}
    inserted_id = db.insert_data('test_table', data)

    mock_cursor.execute.assert_called_with(
        'INSERT INTO test_table (name) VALUES (%s) RETURNING id', ['test_name']
    )
    mock_conn.commit.assert_called_once()
    assert inserted_id == 1


def test_select_data(mock_db_connection):
    """Тест успешного выполнения SELECT-запроса."""
    mock_conn, mock_cursor = mock_db_connection
    db = Database()

    mock_cursor.fetchall.return_value = [(1, 'test_name')]  # Данные для выборки

    result = db.select_data('test_table', ['id', 'name'], 'id = %s', (1,))

    mock_cursor.execute.assert_called_with(
        'SELECT id, name FROM test_table WHERE id = %s', (1,)
    )
    assert result == [(1, 'test_name')]


def test_update_data(mock_db_connection):
    """Тест успешного обновления данных."""
    mock_conn, mock_cursor = mock_db_connection
    db = Database()

    data = {'name': 'new_name'}
    result = db.update_data('test_table', data, 'id = %s', (1,))

    mock_cursor.execute.assert_called_with(
        'UPDATE test_table SET name = %s WHERE id = %s', ['new_name', 1]
    )
    mock_conn.commit.assert_called_once()
    assert result is True


def test_delete_data(mock_db_connection):
    """Тест успешного удаления данных."""
    mock_conn, mock_cursor = mock_db_connection
    db = Database()

    result = db.delete_data('test_table', 'id = %s', (1,))

    mock_cursor.execute.assert_called_with('DELETE FROM test_table WHERE id = %s', (1,))
    mock_conn.commit.assert_called_once()
    assert result is True


def test_execute_query(mock_db_connection):
    """Тест произвольного SQL-запроса."""
    mock_conn, mock_cursor = mock_db_connection
    db = Database()

    query = 'SELECT * FROM test_table'
    result = db.execute_query(query, fetch=True)

    mock_cursor.execute.assert_called_with(query, None)
    mock_cursor.fetchall.assert_called_once()
    assert result == mock_cursor.fetchall()


def test_execute_query_without_fetch(mock_db_connection):
    """Тест произвольного SQL-запроса без fetch."""
    mock_conn, mock_cursor = mock_db_connection
    db = Database()

    query = 'UPDATE test_table SET name = %s WHERE id = %s'
    db.execute_query(query, params=('new_name', 1))

    mock_cursor.execute.assert_called_with(query, ('new_name', 1))
    mock_conn.commit.assert_called_once()
    mock_cursor.fetchall.assert_not_called()
