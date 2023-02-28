from typing import Protocol
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense, AddExpenseItem
from bookkeeper.repository.sqlite_repository import SqliteRepository


class AbstractBookkeeper(Protocol):
    def add_expense(self, expense: AddExpenseItem) -> None:
        pass

    def get_all_expenses(self) -> list[Expense]:
        pass

    def get_cat_by_id(self, id: int) -> Category:
        pass

    def get_cat_id_by_name(self, name: str) -> int:
        pass


class AbstractView(Protocol):
    def set_category_list(self, categories: list[Category]) -> None:
        pass

    def set_bookkeeper(self, bk: AbstractBookkeeper) -> None:
        pass


class Bookkeeper:
    def __init__(self, view: AbstractView = None):
        self.view = view
        self.cat_repo = SqliteRepository[Category]("../../Python_23.db.sqbpro", Category)
        self.exp_repo = SqliteRepository[Expense]("../../Python_23.db.sqbpro", Expense)
        self.cats = self.cat_repo.get_all()
        self.view.set_category_list(self.cats)

    def add_expense(self, expense: AddExpenseItem):
        self.exp_repo.add(Expense(expense.amount, expense.category))

    def get_all_expenses(self):
        return self.exp_repo.get_all()

    def get_cat_by_id(self, id: int):
        return self.cat_repo.get(id)

    def get_cat_id_by_name(self, name: str):
        cat = self.cat_repo.get_all({'name':name})
        if len(cat) == 0:
            return 0
        return cat[0].pk
