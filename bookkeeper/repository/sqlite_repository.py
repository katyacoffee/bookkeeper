from inspect import get_annotations
from typing import Any
from dataclasses import dataclass
import sqlite3 as sql

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SqliteRepository(AbstractRepository[T]):

    def __init__(self, db: str, cls: type) -> None:
        self.db_addr = db
        self.table_name = cls.__name__.lower()
        self.columns = get_annotations(cls, eval_str=True)
        self.columns.pop('pk')
        self.table_created = False

    def add(self, obj: T) -> int:
        """
        Добавить объект в репозиторий, вернуть id объекта,
        также записать id в атрибут pk.
        """
        conn = sql.connect(self.db_addr)
        executer = conn.cursor()
        col_names = ', '.join(self.columns.keys())
        placeholders = ', '.join("?" * len(self.columns))
        vals = [getattr(obj, x) for x in self.columns]
        if not self.table_created:
            cols = []
            for x in self.columns:
                attr = getattr(obj, x)
                res_str = f'{x} '
                type_str = "text"
                if type(attr) is int:
                    type_str = "int"
                res_str += type_str
                cols.append(res_str)

            columns = ', '.join(cols)
            q = f'CREATE TABLE IF NOT EXISTS {self.table_name} (id int PRIMARY KEY, {columns})'
            executer.execute(q)
            self.table_created = True

        executer.execute(f'INSERT INTO {self.table_name} ({col_names}) VALUES ({placeholders})', vals)
        obj.pk = executer.lastrowid
        conn.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        conn = sql.connect(self.db_addr)
        obj = conn.cursor().execute(f'SELECT * FROM {self.table_name} WHERE id = {pk}')
        result = obj.fetchone()
        conn.close()
        return result

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        pass

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
        conn = sql.connect(self.db_addr)
        conn.cursor().execute(f'UPDATE {self.table_name} SET {obj.get_update_statement()} WHERE id = {obj.pk}')
        conn.close()

    def delete(self, pk: int) -> None:
        """ Удалить запись """
        conn = sql.connect(self.db_addr)
        conn.cursor().execute(f'DELETE FROM {self.table_name} WHERE id = {pk}')
        conn.close()
