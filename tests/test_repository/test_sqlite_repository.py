from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.repository.abstract_repository import Model

import pytest


@pytest.fixture
def custom_class():
    class Custom(Model):
        pk: int = 0
        test_str: str = "aaa"
        test_int: int = 123

        def __eq__(self, other) -> bool:
            if self.pk != other.pk:
                return False
            if self.test_str != other.test_str:
                return False
            if self.test_int != other.test_int:
                return False
            return True

    return Custom


@pytest.fixture
def repo(custom_class):
    db = "../../Python_23.db.sqbpro"
    return SqliteRepository(db, custom_class)


def test_crud(repo, custom_class):
    obj = custom_class()
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class()
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) is None


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_delete_unexistent(repo):
    with pytest.raises(KeyError):
        repo.delete(1)


def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)


def test_get_all(repo, custom_class):
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects


def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.test_str = str(i)
        o.test_int = 54321
        repo.add(o)
        objects.append(o)
    assert repo.get_all({'test_str': '0'}) == [objects[0]]
    assert repo.get_all({'test_int': 54321}) == objects
