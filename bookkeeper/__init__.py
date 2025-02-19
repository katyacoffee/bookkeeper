from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense, AddExpenseItem
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.view.bookkeeper import AbstractView


class Bookkeeper:
    def __init__(self, view: AbstractView = None):
        self.view = view
        self.cat_repo = SqliteRepository[Category]("../../Python_23.db.sqbpro", Category)
        self.exp_repo = SqliteRepository[Expense]("../../Python_23.db.sqbpro", Expense)
        self.cats = self.cat_repo.get_all()
        self.view.set_category_list(self.cats)

    def add_expense(self, expense: AddExpenseItem) -> None:
        self.exp_repo.add(Expense(expense.amount, expense.category))

    def add_category(self, name: str, parent: int = 0) -> None:
        self.cat_repo.add(Category(name, parent))

    def get_all_expenses(self) -> list[Expense]:
        return self.exp_repo.get_all()

    def get_all_categories(self) -> list[Category]:
        return self.cat_repo.get_all()

    def get_cat_by_id(self, pk: int) -> Category | None:
        return self.cat_repo.get(pk)

    def get_cat_id_by_name(self, name: str) -> int:
        cat = self.cat_repo.get_all({'name': name})
        if len(cat) == 0:
            return 0
        return cat[0].pk

    def del_all_expenses(self) -> None:
        self.exp_repo.delete_all()

    def del_all_cats(self) -> None:
        self.cat_repo.delete_all()

    def del_cat(self, cat: str) -> None:
        cats = self.cat_repo.get_all({'name': cat})
        if len(cats) == 0:
            return
        category = cats[0]
        children = self.get_all_child_cats(category.pk)
        for c in children:
            exps = self.get_expenses_with_cat(c.name)
            self.delete_expenses(exps)
            self.del_cat(c.name)
        self.cat_repo.delete(category.pk)

    def update_expense(self, date: str, cat: str, comment: str) -> None:
        cat_id = self.get_cat_id_by_name(cat)
        if cat_id == 0:
            return
        exps = self.exp_repo.get_all({'added_date': date, 'category': cat_id})
        if len(exps) == 0:
            return
        new_exp = exps[0]
        new_exp.comment = comment
        self.exp_repo.update(new_exp)

    def get_expenses_with_cat(self, cat: str) -> list[Expense]:
        exps = self.exp_repo.get_all({'category': cat})
        return exps

    def set_expenses_with_new_cat(self, exps: list[Expense], cat: int) -> None:
        for e in exps:
            e.category = cat
            self.exp_repo.update(e)

    def delete_expenses(self, exps: list[Expense]) -> None:
        for e in exps:
            self.exp_repo.delete(e.pk)

    def get_all_child_cats(self, cat_id: int) -> list[Category]:
        return self.cat_repo.get_all({'parent': f'{cat_id}'})
