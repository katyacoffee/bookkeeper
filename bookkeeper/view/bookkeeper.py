from typing import Protocol
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.sqlite_repository import SqliteRepository


class AbstractView(Protocol):
    def set_category_list(self, categories: list[Category]) -> None:
        pass


class Bookkeeper: # не будем называть его Presenter
    def __init__(self, view: AbstractView):
        self.view = view
        self.cat_repo = SqliteRepository[Category]("../../Python_23.db.sqbpro", Category)
        self.exp_repo = SqliteRepository[Expense]("../../Python_23.db.sqbpro", Expense)
        self.cats = self.cat_repo.get_all()
        self.view.set_category_list(self.cats)
