"""
Описан класс, представляющий расходную операцию
"""

from dataclasses import dataclass, field
from datetime import datetime

from ..repository.abstract_repository import Model


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
    amount: int = 0
    category: int = 0
    expense_date: datetime = field(default_factory=datetime.now)
    added_date: datetime = field(default_factory=datetime.now)
    comment: str = ''
    pk: int = 0


@dataclass
class AddExpenseItem:
    category: int = 0
    comment: str = ''
    amount: int = 0
