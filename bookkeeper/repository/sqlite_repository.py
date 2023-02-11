from itertools import count
from typing import Any
import sqlite3 as sql

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SqliteRepository(AbstractRepository[T]):

    def __init__(self, db) -> None:
        self._container: dict[int, T] = {}
        self._counter = count(1)
        self.db = sql.connect(db)
        self.db.cursor().execute("CREATE TABLE aaaaa ..? (...)") # тут нужен запрос на создание таблицы (не забыть, что pk - primary key)

    def add(self, obj: T) -> int:
        """
        Добавить объект в репозиторий, вернуть id объекта,
        также записать id в атрибут pk.
        """
        self.db.cursor().execute('INSERT IN aaaaa VALUES (...)') # тут нужен запрос на вставку строки со значениями obj (т.е. pk, сумма, категория, дата и т.д.)
        obj.pk = self.db.cursor().lastrowid # проверить, что lastrowid действительно возвращает последний айдишник
        return obj.pk

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        obj = self.db.cursor().execute('SELECT * FROM aaaaa WHERE id = ...') # тут нужно вставить в строку айдишник
        return None # а тут надо сначала получить строчку из базы, а потом создать obj

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """

    def delete(self, pk: int) -> None:
        """ Удалить запись """