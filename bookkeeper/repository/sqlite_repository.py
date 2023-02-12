from itertools import count
from typing import Any
import sqlite3 as sql

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SqliteRepository(AbstractRepository[T]):

    def __init__(self, db) -> None:
        self._container: dict[int, T] = {}
        self._counter = count(1)
        self.db = sql.connect(db)
        self.db.cursor().execute(f'CREATE TABLE IF NOT EXISTS {T.get_table_name()} (id int PRIMARY KEY, {T.get_columns()})')
        #self.db.cursor().execute("CREATE TABLE IF NOT EXISTS Expense (id int PRIMARY KEY, amount int, category int, expense_date text, added_date text, comment varchar(255))")

    def add(self, obj: T) -> int:
        """
        Добавить объект в репозиторий, вернуть id объекта,
        также записать id в атрибут pk.
        """
        q = f'INSERT INTO {obj.get_table_name()} ({obj.get_insert_columns()}) VALUES ({obj.get_insert_values()})'
        self.db.cursor().execute(q)
        obj.pk = self.db.cursor().lastrowid # проверить, что lastrowid действительно возвращает последний айдишник
        return obj.pk

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        obj = self.db.cursor().execute(f'SELECT * FROM {T.get_table_name()} WHERE id = {pk}')
        return obj.fetchone()

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        pass

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
        self.db.cursor().execute(f'UPDATE {obj.get_table_name()} SET {obj.get_update_statement()} WHERE id = {obj.pk}')

    def delete(self, pk: int) -> None:
        """ Удалить запись """
        self.db.cursor().execute(f'DELETE FROM {T.get_table_name()} WHERE id = {pk}')
