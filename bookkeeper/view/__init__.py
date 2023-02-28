import sys
from dataclasses import dataclass
from typing import Protocol

from PySide6 import QtGui, QtWidgets  # последний - виджет, содержащий все необходимые документы

from bookkeeper.models.category import Category
from bookkeeper.models.expense import AddExpenseItem
from bookkeeper.view.bookkeeper import AbstractBookkeeper


class AbstractWindow(Protocol):
    def update_exp_table(self) -> None:
        pass


# from PySide6.QtWidgets import
class AddExpense(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_expense_item = AddExpenseItem()
        self.bk: AbstractBookkeeper
        self.win: AbstractWindow


        # self.layout = QtWidgets.QHBoxLayout()  # создаем расладку, чтобы поместить в один виджет несколько
        # self.setLayout(self.layout)  # заполнение виджета раскладкой

        self.grid = QtWidgets.QGridLayout()

        self.comment = 'TODO: сделать добавление комментария?'

        sum_text_widget = QtWidgets.QLabel("Сумма")
        self.grid.addWidget(sum_text_widget, 1, 1)

        cat_text_widget = QtWidgets.QLabel("Категория")
        self.grid.addWidget(cat_text_widget, 2, 1)

        self.sum_widget = QtWidgets.QLineEdit('')
        self.sum_widget.setValidator(QtGui.QIntValidator(1, 10000000, self))
        self.grid.addWidget(self.sum_widget, 1, 2)

        self.cat_list_widget = ListWidget()
        self.grid.addWidget(self.cat_list_widget, 2, 2)

        self.btn_edit = QtWidgets.QPushButton('Редактировать')
        self.grid.addWidget(self.btn_edit, 2, 3)
        self.btn_edit.clicked.connect(self.edit_data)

        self.btn_add = QtWidgets.QPushButton('Добавить')
        self.grid.addWidget(self.btn_add, 3, 2)
        self.btn_add.clicked.connect(self.get_data)

        self.setLayout(self.grid)

        # self.amount = QtWidgets.QLineEdit()  # LineEdit позволяет в отличие от TextEdit в одну строчку только набирать
        # self.amount.setPlaceholderText('Сумма')
        # self.amount.setValidator(QtGui.QIntValidator(1, 10000000, self))  # проверяет правильность введенных данных
        # self.layout.addWidget(self.amount)

    def is_filled(self):
        return bool(self.cat_list_widget.get_id() and self.comment and self.sum_widget.text())

    def get_data(self):
        if self.bk is None:
            raise MemoryError('Bookkeeper is not initialised')
        sum_text = self.sum_widget.text()
        if sum_text == '':
            sum_text = '0'
        self.last_expense_item = AddExpenseItem(self.cat_list_widget.get_id(), self.comment, int(sum_text))
        self.sum_widget.clear()
        self.bk.add_expense(self.last_expense_item)
        self.win.update_exp_table()
        print(self.last_expense_item)
        return

    def edit_data(self):
        pass

    def set_category_list(self, categories: list[Category]) -> None:
        self.cat_list_widget.set_category_list(categories)

    def set_bookkeeper(self, bk: AbstractBookkeeper):
        self.bk = bk
        self.cat_list_widget.set_bookkeeper(bk)

    def set_window(self, win: AbstractWindow):
        self.win = win


class AddCat(QtWidgets.QLabel):
    def __init__(self, name: str, parent: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setText(name)
        self.cat_name = name
        self.cat_parent = parent

    def is_filled(self):
        return True  # TODO

    def add_data(self):
        pass  # TODO: добавление категории в базу


class ListWidget(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.lines = []
        self.cat_list = []
        self.bk: AbstractBookkeeper


    def add_line(self, cat: Category = Category('Продукты')):
        AddCat(cat.name, cat.parent)
        self.lines.append(cat.name)

    def changeEvent(self, event):
        if all(line != '' for line in self.lines):
            self.add_line()

    def get_data(self):
        return [line.get_data() for line in self.lines]

    def get_id(self) -> int:
        cat_name = self.currentText()
        cat_id = self.bk.get_cat_id_by_name(cat_name)
        return cat_id

    def set_category_list(self, categories: list[Category]) -> None:
        self.cat_list = categories
        for cat in self.cat_list:
            self.add_line(cat)

        self.lines = sorted(self.lines)
        for line in self.lines:
            self.addItem(line)
        self.repaint()

    def set_bookkeeper(self, bk: AbstractBookkeeper):
        self.bk = bk


class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500) # TODO: подобрать размер относительно габаритов экрана

        self.bk: AbstractBookkeeper

        table_label = QtWidgets.QLabel('Последние расходы')

        self.expenses_table = QtWidgets.QTableWidget(4, 20)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split())

        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)

        self.expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.expenses_table.verticalHeader().hide()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(table_label)
        self.layout.addWidget(self.expenses_table)

        table_label_2 = QtWidgets.QLabel('Бюджет')

        self.budget_table = QtWidgets.QTableWidget(2, 3)
        self.budget_table.setColumnCount(2)
        self.budget_table.setRowCount(3)
        self.budget_table.setHorizontalHeaderLabels(
            ['Сумма', 'Бюджет'])
        self.budget_table.setVerticalHeaderLabels(
            ['День', 'Неделя', 'Месяц'])

        header_budget = self.budget_table.horizontalHeader()
        header_budget.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        header_budget.setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)

        self.budget_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        vert_header_budget = self.budget_table.verticalHeader()
        vert_header_budget.setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        vert_header_budget.setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)
        vert_header_budget.setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)

        self.layout.addWidget(table_label_2)
        self.layout.addWidget(self.budget_table)

        # добавить таблицу Бюджета

        self.expense_adder = AddExpense()
        self.expense_adder.set_window(self)
        # self.budget_adder = AddExpense()

        self.layout.addWidget(self.expense_adder)
        # self.layout.addWidget(self.budget_adder)

    def set_data(self, data: list[list[str]]):
        for i, row in enumerate(data):
            for j, x in enumerate(row):
                self.expenses_table.setItem(i, j, QtWidgets.QTableWidgetItem(x.capitalize()))

    def set_category_list(self, categories: list[Category]) -> None:
        self.expense_adder.set_category_list(categories)

    def set_bookkeeper(self, bk: AbstractBookkeeper):
        self.bk = bk
        self.expense_adder.set_bookkeeper(bk)
        self.update_exp_table()

    def update_exp_table(self):
        all_exp = self.bk.get_all_expenses()
        i = len(all_exp)
        for exp in all_exp:
            i -= 1
            if i >= self.expenses_table.rowCount():
                continue
            cat_name = 'None'
            if int(exp.category) > 0:
                cat = self.bk.get_cat_by_id(exp.category)
                if cat is not None:
                    cat_name = cat.name
            self.expenses_table.setItem(i, 0, QtWidgets.QTableWidgetItem(f'{exp.expense_date}'))
            self.expenses_table.setItem(i, 1, QtWidgets.QTableWidgetItem(f'{exp.amount}'))
            self.expenses_table.setItem(i, 2, QtWidgets.QTableWidgetItem(cat_name))
            self.expenses_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f'{exp.comment}'))

            if i == 0:
                break


class View:
    def __init__(self):
        self.window = MainWindow()
        self.bk: AbstractBookkeeper

    def show(self):
        self.window.show()

    def set_category_list(self, categories: list[Category]) -> None:
        self.window.set_category_list(categories)

    def set_bookkeeper(self, bk: AbstractBookkeeper):
        self.bk = bk
        self.window.set_bookkeeper(bk)
