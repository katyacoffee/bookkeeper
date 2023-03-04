from typing import Protocol
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense, AddExpenseItem
from bookkeeper.repository.sqlite_repository import SqliteRepository


class AbstractBookkeeper(Protocol):
    def add_expense(self, expense: AddExpenseItem) -> None:
        pass

    def add_category(self, name: str, parent: int) -> None:
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

    def add_category(self, name: str, parent: int):
        self.cat_repo.add(Category(name, parent))

    def get_all_expenses(self):
        return self.exp_repo.get_all()

    def get_all_categories(self):
        return self.cat_repo.get_all()

    def get_cat_by_id(self, id: int):
        return self.cat_repo.get(id)

    def get_cat_id_by_name(self, name: str):
        cat = self.cat_repo.get_all({'name': name})
        if len(cat) == 0:
            return 0
        return cat[0].pk

    def del_all_expenses(self):
        self.exp_repo.delete_all()

    def del_cat(self, cat: str):
        cats = self.cat_repo.get_all({'name': cat})
        if len(cats) == 0:
            return
        self.cat_repo.delete(cats[0].pk)

    def update_expense(self, date: str, cat: str, comment: str):
        cat_id = self.get_cat_id_by_name(cat)
        if cat_id == 0:
            return
        exps = self.exp_repo.get_all({'added_date': date, 'category': cat_id})
        if len(exps) == 0:
            return
        new_exp = exps[0]
        new_exp.comment = comment
        self.exp_repo.update(new_exp)
