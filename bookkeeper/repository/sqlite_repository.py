from inspect import get_annotations
from typing import Any
import sqlite3 as sql
from datetime import datetime

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SqliteRepository(AbstractRepository[T]):

    def __init__(self, db: str, cls: type) -> None:
        self.db_addr = db
        self.table_name = cls.__name__.lower()
        self.columns = get_annotations(cls, eval_str=True)
        self.columns.pop('pk')
        self.cls_type = cls

        conn = sql.connect(self.db_addr)
        with conn:
            cols = []
            for x in self.columns:
                attr = getattr(cls, x)
                res_str = f'{x} '
                type_str = "TEXT"
                if type(attr) is int:
                    type_str = "INTEGER"
                res_str += type_str
                cols.append(res_str)

            columns = ', '.join(cols)
            q = f'CREATE TABLE IF NOT EXISTS {self.table_name} ' \
                f'(id INTEGER PRIMARY KEY, {columns})'
            conn.cursor().execute(q)
        conn.close()

    def add(self, obj: T) -> int:
        """
        Добавить объект в репозиторий, вернуть id объекта,
        также записать id в атрибут pk.
        """
        if type(obj) is not self.cls_type:
            raise ValueError("invalid object")
        if obj.pk != 0:
            raise ValueError("pk != 0")
        col_names = ', '.join(self.columns.keys())
        vals = [getattr(obj, x) for x in self.columns]
        insert_str = ''
        i = 0
        for v in vals:
            if i > 0:
                insert_str += ', '
            if type(v) is str or type(v) is datetime:
                new_v = f'{v}'
                if type(v) is datetime:
                    index = -1
                    try:
                        index = new_v.index('.')
                    except ValueError:
                        pass
                    if index > 0:
                        new_v = new_v[:index]
                new_v = '\'' + new_v + '\''
                insert_str += new_v
            elif v is None:
                insert_str += '0'
            else:
                insert_str += f'{v}'
            i += 1
        conn = sql.connect(self.db_addr)
        with conn:
            q = f'INSERT INTO {self.table_name} ({col_names}) VALUES ({insert_str})'
            pk = conn.cursor().execute(q).lastrowid
            obj.pk = pk
        conn.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        conn = sql.connect(self.db_addr)
        with conn:
            result = conn.cursor().execute(f'SELECT * FROM {self.table_name} '
                                           f'WHERE id = {pk}').fetchall()
            res_obj = self.cls_type()
            for r in result:
                i = 1
                for x in self.columns:
                    setattr(res_obj, x, r[i])
                    i += 1
                res_obj.pk = r[0]
            if len(result) == 0:
                res_obj = None

        conn.close()
        return res_obj

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        if where is None:
            conn = sql.connect(self.db_addr)
            with conn:
                result = conn.cursor().execute(f'SELECT * FROM {self.table_name}').\
                    fetchall()
                objects = []
                for r in result:
                    res_obj = self.cls_type()
                    i = 1
                    for x in self.columns:
                        setattr(res_obj, x, r[i])
                        i += 1
                    res_obj.pk = r[0]
                    objects.append(res_obj)

            conn.close()
            return objects
        else:
            condition = ''
            i = 0
            for k, v in where.items():
                if i > 0:
                    condition += ' AND '
                condition += k + ' = '
                val = f'{v}'
                if type(v) == str:
                    val = '\'' + val + '\''
                condition += val
                i += 1

            conn = sql.connect(self.db_addr)
            with conn:
                result = conn.cursor().execute(f'SELECT * FROM {self.table_name} '
                                               f'WHERE {condition}').fetchall()
                objects = []
                for r in result:
                    res_obj = self.cls_type()
                    i = 1
                    for x in self.columns:
                        setattr(res_obj, x, r[i])
                        i += 1
                    res_obj.pk = r[0]
                    objects.append(res_obj)

            conn.close()
            return objects

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
        if obj.pk == 0:
            raise ValueError("invalid pk")
        conn = sql.connect(self.db_addr)
        with conn:
            cols = []
            for x in self.columns:
                attr = getattr(obj, x)
                if type(attr) is str:
                    attr = '\'' + attr + '\''
                cols.append(f'{x} = {attr}')

            update_statement = ', '.join(cols)
            conn.cursor().execute(f'UPDATE {self.table_name} SET {update_statement} '
                                  f'WHERE id = {obj.pk}')
        conn.close()

    def delete(self, pk: int) -> None:
        """ Удалить запись """
        conn = sql.connect(self.db_addr)
        with conn:
            result = conn.cursor().execute(f'SELECT * FROM {self.table_name} '
                                           f'WHERE id = {pk}').fetchall()
            if len(result) == 0:
                raise KeyError("not found")
            conn.cursor().execute(f'DELETE FROM {self.table_name} WHERE id = {pk}')
        conn.close()

    def delete_all(self) -> None:
        """ Очистка таблицы """
        conn = sql.connect(self.db_addr)
        with conn:
            conn.cursor().execute(f'DELETE FROM {self.table_name}')
        conn.close()
