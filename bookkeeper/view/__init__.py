import sys, time
from dataclasses import dataclass
from typing import Protocol
from datetime import datetime as dt
import datetime

from PySide6 import QtGui, QtWidgets, QtCore  # последний - виджет, содержащий все необходимые документы
from PySide6.QtWidgets import QComboBox, QStyle, QMessageBox
from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QRegularExpressionValidator

from bookkeeper.models.category import Category
from bookkeeper.models.expense import AddExpenseItem
from bookkeeper.view.bookkeeper import AbstractBookkeeper


class AbstractWindow(Protocol):
    def update_exp_table(self) -> None:
        pass

    def update_bud_table(self) -> None:
        pass

    def open_editor(self) -> None:
        pass

    def set_budget(self, period: str, amount: int) -> None:
        pass

    def update_cat_table(self) -> None:
        pass

    def add_new_cat(self, name: str, parent: int) -> None:
        pass


# from PySide6.QtWidgets import
class AddExpense(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_expense_item = AddExpenseItem()
        self.bk: AbstractBookkeeper
        self.win: AbstractWindow

        self.grid = QtWidgets.QGridLayout()

        self.comment = ''

        self.sum_text_widget = QtWidgets.QLabel("Сумма")
        self.grid.addWidget(self.sum_text_widget, 1, 1)

        self.cat_text_widget = QtWidgets.QLabel("Категория")
        self.grid.addWidget(self.cat_text_widget, 2, 1)

        self.sum_widget = QtWidgets.QLineEdit('')
        self.sum_widget.setValidator(QtGui.QIntValidator(1, 10000000, self))
        self.sum_widget.setStyleSheet('border-radius: 5px;')
        self.grid.addWidget(self.sum_widget, 1, 2)

        self.cat_list_widget = ListWidget()
        self.grid.addWidget(self.cat_list_widget, 2, 2)
        self.cat_list_widget.setStyleSheet('border-radius: 5px; border: 1px solid gray; padding: 1px 18px 1px 3px; min-width: 6em;')

        self.btn_edit = QtWidgets.QPushButton('Редактировать')
        self.grid.addWidget(self.btn_edit, 2, 3)
        self.btn_edit.setStyleSheet('QPushButton { background-color: #CDAF95; border-radius: 5px; height: 20px; width: 350px; }'
                                    'QPushButton:pressed { background-color: #808A87 }')
        self.btn_edit.clicked.connect(self.edit_data)

        self.btn_add = QtWidgets.QPushButton('Добавить')
        self.grid.addWidget(self.btn_add, 3, 2)
        self.btn_add.setGeometry(10, 10, 30, 30)
        self.btn_add.setStyleSheet('QPushButton { background-color: #CDAF95; border-radius: 5px; height: 20px; }'
                                   'QPushButton:pressed { background-color: #808A87 }')
        self.btn_add.clicked.connect(self.get_data)

        self.setLayout(self.grid)

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
        self.win.update_bud_table()
        print(self.last_expense_item)
        return

    def edit_data(self):
        self.win.open_editor()

    def set_category_list(self, categories: list[Category]) -> None:
        self.cat_list_widget.set_category_list(categories)

    def set_bookkeeper(self, bk: AbstractBookkeeper):
        self.bk = bk
        self.cat_list_widget.set_bookkeeper(bk)

    def set_window(self, win: AbstractWindow):
        self.win = win


class ListWidget(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.lines = []
        self.cat_list = []
        self.bk: AbstractBookkeeper

    def add_line(self, cat: Category = Category('Продукты')):
        self.lines.append(cat.name)

    def get_data(self):
        return [line.get_data() for line in self.lines]

    def get_id(self) -> int:
        cat_name = self.currentText()
        cat_id = self.bk.get_cat_id_by_name(cat_name)
        return cat_id

    def set_category_list(self, categories: list[Category]) -> None:
        self.cat_list = categories
        self.lines = []
        for cat in self.cat_list:
            self.add_line(cat)

        self.lines = sorted(self.lines)
        self.clear()
        for line in self.lines:
            self.addItem(line)
        self.repaint()

    def set_bookkeeper(self, bk: AbstractBookkeeper):
        self.bk = bk


class EditorWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        self.setWindowTitle('Edit')
        self.parentWindow: AbstractWindow
        self.bk: AbstractBookkeeper

        self.grid = QtWidgets.QGridLayout()

        self.cat_list_widget = ListWidget()
        self.grid.addWidget(self.cat_list_widget, 2, 1)
        self.cat_list_widget.setStyleSheet('border-radius: 5px; border: 1px solid gray; padding: 1px 18px 1px 3px; min-width: 6em;')

        self.ed_text_widget = QtWidgets.QLabel("Редактировать категорию")
        self.grid.addWidget(self.ed_text_widget, 1, 1)
        self.ed_text_widget.setStyleSheet('font-weight: bold;')

        self.btn_del_cat = QtWidgets.QPushButton('Удалить категорию')
        self.grid.addWidget(self.btn_del_cat, 2, 2)
        self.btn_del_cat.setStyleSheet('QPushButton {background-color: #EE6363;border-radius: 5px; height: 20px; width: 140px; font-weight: bold }'
                                       'QPushButton:hover { background-color: #CD5555 }')
        self.btn_del_cat.clicked.connect(self.call_del_cat_question)

        self.new1_text_widget = QtWidgets.QLabel("Новая категория")
        self.grid.addWidget(self.new1_text_widget, 3, 1)

        self.new2_text_widget = QtWidgets.QLabel("Родительская категория")
        self.grid.addWidget(self.new2_text_widget, 3, 2)

        self.new1_widget = QtWidgets.QLineEdit('')
        self.t = QRegularExpressionValidator(QRegularExpression('[а-я-А-Я-a-z-A-Z-0-9 ]+'))
        self.new1_widget.setValidator(self.t)
        self.new1_widget.setStyleSheet('border-radius: 5px;')
        self.grid.addWidget(self.new1_widget, 4, 1)

        self.new2_widget = QtWidgets.QLineEdit('')
        self.new2_widget.setValidator(self.t)
        self.new2_widget.setStyleSheet('border-radius: 5px;')
        self.grid.addWidget(self.new2_widget, 4, 2)

        self.btn_add1 = QtWidgets.QPushButton('Добавить')
        self.grid.addWidget(self.btn_add1, 4, 3)
        self.btn_add1.setStyleSheet('QPushButton { background-color: #6495ED; border-radius: 5px; height: 20px; width: 100px; }'
                                    'QPushButton:pressed { background-color: #3D59AB }')
        self.btn_add1.clicked.connect(self.add_cat)

        self.ed_bud_text_widget = QtWidgets.QLabel("Редактировать бюджет")
        self.grid.addWidget(self.ed_bud_text_widget, 5, 1)
        self.ed_bud_text_widget.setStyleSheet('font-weight: bold;')

        self.btn_del_bud = QtWidgets.QPushButton('Удалить все расходы')
        self.grid.addWidget(self.btn_del_bud, 6, 1)
        self.btn_del_bud.setStyleSheet('QPushButton { background-color: #EE6363; border-radius: 5px; height: 20px; width: 140px; font-weight: bold }'
                                       'QPushButton:hover { background-color: #CD5555 }')
        self.btn_del_bud.clicked.connect(self.call_del_all_question)

        new_bud_text_widget = QtWidgets.QLabel("Задать бюджет")
        self.grid.addWidget(new_bud_text_widget, 7, 1)

        self.combobox1 = QComboBox()
        self.combobox1.addItem('День')
        self.combobox1.addItem('Неделя')
        self.combobox1.addItem('Месяц')
        self.combobox1.setStyleSheet('border-radius: 5px; border: 1px solid gray; padding: 1px 18px 1px 3px; min-width: 6em;')

        self.grid.addWidget(self.combobox1, 8, 1)

        self.add_bud_widget = QtWidgets.QLineEdit('')
        self.add_bud_widget.setValidator(QtGui.QIntValidator(1, 1000000, self))
        self.add_bud_widget.setStyleSheet('border-radius: 5px;')
        self.grid.addWidget(self.add_bud_widget, 8, 2)

        self.btn_add_bud = QtWidgets.QPushButton('Задать')
        self.grid.addWidget(self.btn_add_bud, 8, 3)
        self.btn_add_bud.setStyleSheet('QPushButton { background-color: #6495ED; border-radius: 5px; height: 20px; width: 100px; }'
                                       'QPushButton:pressed { background-color: #3D59AB }')
        self.btn_add_bud.clicked.connect(self.get_bud_data)

        self.setLayout(self.grid)

    def set_parent_window(self, win: AbstractWindow):
        self.parentWindow = win

    def set_category_list(self, categories: list[Category]) -> None:
        self.cat_list_widget.set_category_list(categories)

    def set_bookkeeper(self, bk: AbstractBookkeeper):
        self.bk = bk

    def call_del_all_question(self):
        ans = QMessageBox.question(self, 'Очистить расходы', "Вы уверены, что хотите удалить все расходы?")
        self.del_all_expenses(ans)

    def del_all_expenses(self, button):
        if button == QMessageBox.No:
            return
        self.bk.del_all_expenses()
        self.parentWindow.update_exp_table()
        self.parentWindow.update_bud_table()

    def get_bud_data(self):
        bud = self.add_bud_widget.text()
        if bud == '':
            bud = '0'
        period = self.combobox1.currentText()
        self.parentWindow.set_budget(period, int(bud))
        f = open("budget.txt", "w")
        f.write(self.parentWindow.budget_table.item(0, 1).text() + ',')
        f.write(self.parentWindow.budget_table.item(1, 1).text() + ',')
        f.write(self.parentWindow.budget_table.item(2, 1).text())

    def call_del_cat_question(self):
        ans = QMessageBox.question(self, 'Удалить категорию', "Вы уверены, что хотите удалить категорию?")
        self.del_cat(ans)

    def del_cat(self, button):
        if button == QMessageBox.No:
            return
        cat_name = self.cat_list_widget.currentText()
        pk = self.bk.get_cat_id_by_name(cat_name)
        if pk == 0:
            return
        category = self.bk.get_cat_by_id(pk)
        exp_with_cat = self.bk.get_expenses_with_cat(category.name)
        parent = int(category.parent)
        if parent > 0:
            self.bk.set_expenses_with_new_cat(exp_with_cat, parent)
            par_cat_name = 'None'
            parent_cat = self.bk.get_cat_by_id(parent)
            if parent_cat is not None:
                par_cat_name = parent_cat.name
            QMessageBox.information(self, 'Категория удалена',
                                    "Категория '" + cat_name + "' удалена. Расходы перемещены на родительскую категорию '" +
                                    par_cat_name + "'")
        else:
            QMessageBox.information(self, 'Категория удалена',
                                    "Категория '" + cat_name + "' удалена. Расходы, связанные с ней, также удалены.")
        self.bk.del_cat(cat_name)
        cats = self.bk.get_all_categories()
        self.cat_list_widget.set_category_list(cats)
        self.parentWindow.update_cat_table()
        self.parentWindow.update_exp_table()
        self.parentWindow.update_bud_table()

    def add_cat(self):
        newcat = self.new1_widget.text()
        parcat = self.new2_widget.text()
        if parcat == '':
            self.bk.add_category(newcat, 0)
            QMessageBox.information(self, 'Категория добавлена',
                                    "Новая категория '" + newcat + "' успешно добавлена")
        else:
            found_id = self.bk.get_cat_id_by_name(parcat)
            if found_id == 0:
                QMessageBox.critical(self, 'Категория не найдена',
                                        "Родительская категория '" + parcat + "' не найдена!")
            else:
                self.bk.add_category(newcat, found_id)
                QMessageBox.information(self, 'Категория добавлена',
                                        "Новая подкатегория '" + newcat + "' категории '" + parcat + "' успешно добавлена")

        cats = self.bk.get_all_categories()
        self.cat_list_widget.set_category_list(cats)
        self.parentWindow.update_cat_table()
        self.new1_widget.clear()


class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.showMaximized()
        self.setWindowTitle('Bookkeeper')

        self.bk: AbstractBookkeeper
        self.editor = EditorWindow()
        self.categories: list[Category]

        table_label = QtWidgets.QLabel('Последние расходы')

        self.expenses_table = QtWidgets.QTableWidget(4, 20)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split())

        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)

        self.expenses_table.verticalHeader().hide()

        self.expenses_table.setStyleSheet('border: 1px solid gray;')

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(table_label)
        self.layout.addWidget(self.expenses_table)

        self.bud_layout = QtWidgets.QGridLayout()

        self.btn_add_comm = QtWidgets.QPushButton('Добавить комментарии')
        self.btn_add_comm.setStyleSheet('QPushButton { background-color: #CDAF95; border-radius: 5px; height: 20px; width: 150px; }'
                                   'QPushButton:pressed { background-color: #808A87 }')
        self.btn_add_comm.setMaximumWidth(350)
        self.btn_add_comm.clicked.connect(self.save_comments)
        self.bud_layout.addWidget(self.btn_add_comm, 0, 1)

        self.table_label_2 = QtWidgets.QLabel('Бюджет')
        self.bud_layout.addWidget(self.table_label_2, 0, 0)

        self.layout.addLayout(self.bud_layout)

        self.budget_table = QtWidgets.QTableWidget(2, 3)
        self.budget_table.setColumnCount(2)
        self.budget_table.setRowCount(3)
        self.budget_table.setHorizontalHeaderLabels(
            ['Сумма', 'Бюджет'])
        self.budget_table.setVerticalHeaderLabels(
            ['День', 'Неделя', 'Месяц'])

        header_budget = self.budget_table.horizontalHeader()
        header_budget.setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
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

        item1 = QtWidgets.QTableWidgetItem('Сумма')
        item1.setBackground(QtGui.QColor(205, 175, 149))
        self.budget_table.setHorizontalHeaderItem(0, item1)

        item2 = QtWidgets.QTableWidgetItem('Бюджет')
        item2.setBackground(QtGui.QColor(205, 175, 149))
        self.budget_table.setHorizontalHeaderItem(1, item2)

        self.budget_table.setStyleSheet('border: 1px solid gray; border-radius: 5px;')

        self.layout.addWidget(self.budget_table)

        self.expense_adder = AddExpense()
        self.expense_adder.set_window(self)

        self.layout.addWidget(self.expense_adder)

    def set_data(self, data: list[list[str]]):
        for i, row in enumerate(data):
            for j, x in enumerate(row):
                self.expenses_table.setItem(i, j, QtWidgets.QTableWidgetItem(x.capitalize()))

    def set_category_list(self, categories: list[Category]) -> None:
        self.expense_adder.set_category_list(categories)
        self.categories = categories

    def set_bookkeeper(self, bk: AbstractBookkeeper):
        self.bk = bk
        self.expense_adder.set_bookkeeper(bk)
        self.editor.set_bookkeeper(bk)
        self.update_exp_table()
        self.update_bud_table()

    def update_exp_table(self):
        i = 0
        while i < self.expenses_table.rowCount():
            for j in range(0,4):
                empty_item = QtWidgets.QTableWidgetItem('')
                empty_item.setFlags(~Qt.ItemIsEditable)
                self.expenses_table.setItem(i, j, empty_item)
            i += 1

        all_exp = self.bk.get_all_expenses()
        exp_with_empty_cat = []
        for exp in all_exp:
            cat = self.bk.get_cat_by_id(exp.category)
            if cat is None:
                exp_with_empty_cat.append(exp)
        if len(exp_with_empty_cat) > 0:
            self.bk.delete_expenses(exp_with_empty_cat)
        i = len(all_exp) - len(exp_with_empty_cat)
        for exp in all_exp:
            i -= 1
            if i >= self.expenses_table.rowCount():
                continue
            cat_name = 'None'
            if int(exp.category) > 0:
                cat = self.bk.get_cat_by_id(exp.category)
                if cat is not None:
                    cat_name = cat.name
            if cat_name == 'None':
                i += 1
                continue
            date = QtWidgets.QTableWidgetItem(f'{exp.expense_date}')
            date.setFlags(date.flags() & ~Qt.ItemIsEditable)
            self.expenses_table.setItem(i, 0, date)
            amount = QtWidgets.QTableWidgetItem(f'{exp.amount}')
            amount.setFlags(amount.flags() & ~Qt.ItemIsEditable)
            self.expenses_table.setItem(i, 1, amount)
            cat = QtWidgets.QTableWidgetItem(cat_name)
            cat.setFlags(cat.flags() & ~Qt.ItemIsEditable)
            self.expenses_table.setItem(i, 2, cat)
            comment = QtWidgets.QTableWidgetItem(f'{exp.comment}')
            comment.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.expenses_table.setItem(i, 3, comment)

            if i == 0:
                break

    def save_comments(self):
        for i in range(0, self.expenses_table.rowCount()):
            comment_item = self.expenses_table.item(i, 3)
            comment = comment_item.text()
            if comment != '':
                cat_name = self.expenses_table.item(i, 2).text()
                date = self.expenses_table.item(i, 0).text()
                self.bk.update_expense(date, cat_name, comment)

    def update_bud_table(self):
        all_exp = self.bk.get_all_expenses()
        exp_day = 0
        exp_week = 0
        exp_month = 0
        for exp in all_exp:
            date = dt.strptime(f'{exp.expense_date}', '%Y-%m-%d %H:%M:%S')
            if date.day == dt.today().day:
                exp_day += int(exp.amount)
            if date >= dt.today() - datetime.timedelta(days=7):
                exp_week += int(exp.amount)
            if date.month == dt.today().month:
                exp_month += int(exp.amount)
        self.budget_table.setItem(0, 0, QtWidgets.QTableWidgetItem(f'{exp_day}'))
        self.budget_table.setItem(1, 0, QtWidgets.QTableWidgetItem(f'{exp_week}'))
        self.budget_table.setItem(2, 0, QtWidgets.QTableWidgetItem(f'{exp_month}'))

        f = open('budget.txt', 'r')
        bud = f.read().split(',')
        for i in range(0, len(bud)):
            self.budget_table.setItem(i, 1, QtWidgets.QTableWidgetItem(f'{bud[i]}'))
            if i == 2:
                break


    def open_editor(self):
        self.editor.set_parent_window(self)
        cats = self.bk.get_all_categories()
        self.editor.set_category_list(cats)
        self.editor.show()

    def set_daily_budget(self, amount: int):
        self.budget_table.setItem(0, 1, QtWidgets.QTableWidgetItem(f'{amount}'))
        self.budget_table.setItem(1, 1, QtWidgets.QTableWidgetItem(f'{amount*7}'))
        self.budget_table.setItem(2, 1, QtWidgets.QTableWidgetItem(f'{amount*30}'))

    def set_weekly_budget(self, amount: int):
        self.budget_table.setItem(0, 1, QtWidgets.QTableWidgetItem(f'{amount // 7}'))
        self.budget_table.setItem(1, 1, QtWidgets.QTableWidgetItem(f'{amount}'))
        self.budget_table.setItem(2, 1, QtWidgets.QTableWidgetItem(f'{amount // 7 * 30}'))

    def set_monthly_budget(self, amount: int):
        self.budget_table.setItem(0, 1, QtWidgets.QTableWidgetItem(f'{amount // 30}'))
        self.budget_table.setItem(1, 1, QtWidgets.QTableWidgetItem(f'{amount // 30 * 7}'))
        self.budget_table.setItem(2, 1, QtWidgets.QTableWidgetItem(f'{amount}'))

    def set_budget(self, period: str, amount: int):
        if period == 'День':
            self.set_daily_budget(amount)
        elif period == 'Неделя':
            self.set_weekly_budget(amount)
        elif period == 'Месяц':
            self.set_monthly_budget(amount)

    def add_new_cat(self, name: str, parent: int):
        self.bk.add_category(name, parent)

    def update_cat_table(self):
        cats = self.bk.get_all_categories()
        self.expense_adder.set_category_list(cats)
        self.editor.set_category_list(cats)


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
