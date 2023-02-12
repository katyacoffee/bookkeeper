"""
Описан класс, представляющий расходную операцию
"""

from dataclasses import dataclass, field
from datetime import datetime

from ..repository.abstract_repository import Model, DBWrap


@dataclass(slots=True)
class Expense(Model):
    """
    Расходная операция.
    amount - сумма
    category - id категории расходов
    expense_date - дата расхода
    added_date - дата добавления в бд
    comment - комментарий
    pk - id записи в базе данных
    """
    amount: int
    category: int
    expense_date: datetime = field(default_factory=datetime.now)
    added_date: datetime = field(default_factory=datetime.now)
    comment: str = ''
    pk: int = 0


@dataclass(slots=True)
class ExpenseWrap(Expense, DBWrap):

    def get_update_statement(self) -> str:
        return f'amount = {self.amount}, category = {self.category}, expense_date = {self.expense_date}, added_date = {self.added_date}, comment = {self.comment}'