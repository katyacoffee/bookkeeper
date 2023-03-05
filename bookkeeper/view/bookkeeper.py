from typing import Protocol
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense, AddExpenseItem
from bookkeeper.repository.sqlite_repository import SqliteRepository


class AbstractBookkeeper(Protocol):
    def add_expense(self, expense: AddExpenseItem) -> None:
        pass

    def add_category(self, name: str, parent: int = 0) -> None:
        pass

    def get_all_expenses(self) -> list[Expense]:
        pass

    def get_all_categories(self) -> list[Category]:
        pass

    def get_cat_by_id(self, id: int) -> Category:
        pass

    def get_cat_id_by_name(self, name: str) -> int:
        pass

    def del_all_expenses(self) -> None:
        pass

    def del_cat(self, cat: str) -> None:
        pass

    def update_expense(self, date: str, cat: str, comment: str) -> None:
        pass

    def get_expenses_with_cat(self, cat: str) -> list[Expense]:
        pass

    def set_expenses_with_new_cat(self, exps: list[Expense], cat: int) -> None:
        pass

    def delete_expenses(self, exps: list[Expense]) -> None:
        pass


class AbstractView(Protocol):
    def set_category_list(self, categories: list[Category]) -> None:
        pass

    def set_bookkeeper(self, bk: AbstractBookkeeper) -> None:
        pass
