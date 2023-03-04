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

    def question_del(self) -> None:  #TEST
        pass  #TEST

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


        # self.layout = QtWidgets.QHBoxLayout()  # создаем расладку, чтобы поместить в один виджет несколько
        # self.setLayout(self.layout)  # заполнение виджета раскладкой

        self.grid = QtWidgets.QGridLayout()

        self.comment = 'TODO: сделать добавление комментария?'

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

    # def question_win(self, queswin: AbstractWindow):  # TEST
    #     self.queswin = queswin  # TEST


class AddCat(QtWidgets.QLabel):
    def __init__(self, name: str, parent: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setText(name)
        self.cat_name = name
        self.cat_parent = parent

    # def is_filled(self):
    #     return True  # TODO

    def add_data(self, name: str, parent: int) -> None:
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

        # self.layout = QtWidgets.QVBoxLayout()
        # self.setLayout(self.layout)

        self.cat_list_widget = ListWidget()
        # self.layout.addWidget(self.cat_list_widget, 2, 1)
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
        # self.new1_widget.setText('')
        self.t = QRegularExpressionValidator(QRegularExpression('[а-я-А-Я-a-z-A-Z ]+'))
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

        # self.cat_list_widget = ListWidget()
        # # self.layout.addWidget(self.cat_list_widget, 2, 1)
        # self.grid.addWidget(self.cat_list_widget, 8, 1)

        self.combobox1 = QComboBox()
        self.combobox1.addItem('День')
        self.combobox1.addItem('Неделя')
        self.combobox1.addItem('Месяц')
        self.combobox1.setStyleSheet('border-radius: 5px; border: 1px solid gray; padding: 1px 18px 1px 3px; min-width: 6em;')

        # layout = QVBoxLayout()
        self.grid.addWidget(self.combobox1, 8, 1)

        # container = QWidget()
        # container.setLayout(layout)

        self.add_bud_widget = QtWidgets.QLineEdit('')
        self.add_bud_widget.setValidator(QtGui.QIntValidator(1, 1000000, self))
        self.add_bud_widget.setStyleSheet('border-radius: 5px;')
        self.grid.addWidget(self.add_bud_widget, 8, 2)

        self.btn_add_bud = QtWidgets.QPushButton('Задать')
        self.grid.addWidget(self.btn_add_bud, 8, 3)
        self.btn_add_bud.setStyleSheet('QPushButton { background-color: #6495ED; border-radius: 5px; height: 20px; width: 100px; }'
                                       'QPushButton:pressed { background-color: #3D59AB }')
        self.btn_add_bud.clicked.connect(self.get_bud_data)

        #
        # self.cat_list_widget = ListWidget()
        # self.grid.addWidget(self.cat_list_widget, 2, 2)
        #
        # self.btn_edit = QtWidgets.QPushButton('Удалить')
        # self.grid.addWidget(self.btn_edit, 2, 3)
        # self.btn_edit.clicked.connect(self.edit_data)
        #
        # self.btn_add = QtWidgets.QPushButton('Добавить')
        # self.grid.addWidget(self.btn_add, 3, 2)
        # self.btn_add.clicked.connect(self.get_data)
        #
        self.setLayout(self.grid)

    def set_parent_window(self, win: AbstractWindow):
        self.parentWindow = win

    def set_category_list(self, categories: list[Category]) -> None:
        self.cat_list_widget.set_category_list(categories)

    def set_bookkeeper(self, bk: AbstractBookkeeper):
        self.bk = bk

    def call_del_all_question(self):
        msgbox = QMessageBox(self)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("Вы уверены, что хотите удалить все расходы?")
        msgbox.setWindowTitle('Очистить расходы')
        msgbox.addButton(QMessageBox.Yes)
        msgbox.addButton(QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.No)
        msgbox.buttonClicked.connect(self.del_all_expenses)
        msgbox.exec_()

    def del_all_expenses(self, button):
        if button.text() == '&No':
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

    def call_del_cat_question(self):
        msgbox = QMessageBox(self)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setText("Вы уверены, что хотите удалить категорию?")
        msgbox.setWindowTitle('Удалить категорию')
        msgbox.addButton(QMessageBox.Ok)
        msgbox.addButton(QMessageBox.Cancel)
        msgbox.setDefaultButton(QMessageBox.Cancel)
        msgbox.buttonClicked.connect(self.del_cat)
        msgbox.exec_()

    def del_cat(self, button):
        if button.text() == '&Cancel':
            return
        self.bk.del_cat(self.cat_list_widget.currentText())
        self.parentWindow.update_cat_table()

    def add_cat(self):
        newcat = self.new1_widget.text()
        parcat = self.new2_widget.text()
        if parcat == '':
            self.bk.add_category(newcat, 0)
            info_win = QMessageBox(self)
            info_win.setIcon(QMessageBox.Information)
            info_win.addButton(QMessageBox.Ok)
            info_win.setText("Новая категория '" + newcat + "' успешно добавлена")
            info_win.exec_()
        else:
            found_id = self.bk.get_cat_id_by_name(parcat)
            if found_id == 0:
                info_win = QMessageBox(self)
                info_win.setIcon(QMessageBox.Critical)
                info_win.addButton(QMessageBox.Cancel)
                info_win.setText("Родительская категория '" + parcat + "' не найдена!")
                info_win.exec_()
            else:
                self.bk.add_category(newcat, found_id)
                info_win = QMessageBox(self)
                info_win.setIcon(QMessageBox.Information)
                info_win.addButton(QMessageBox.Ok)
                info_win.setText("Новая подкатегория '" + newcat + "' категории '" + parcat + "' успешно добавлена")
                info_win.exec_()

        self.parentWindow.update_cat_table()

    # def open_editor(self):  #???
    #     self.editor = QMessageBox()
    #     self.editor.set_parent_window(self)
    #     self.editor.set_category_list(self.categories)
    #     self.editor.show()

    # def del_cat(self):  #TEST
    #     self.queswin.open_editor()  #TEST


class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.resize(500, 500) # TODO: подобрать размер относительно габаритов экрана
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.showMaximized()  # !
        self.setWindowTitle('Bookkeeper')
        # self.setStyleSheet('background-color: #188')

        self.bk: AbstractBookkeeper
        self.editor = EditorWindow()
        self.categories: list[Category]

        table_label = QtWidgets.QLabel('Последние расходы')

        self.expenses_table = QtWidgets.QTableWidget(4, 20)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        # self.expenses_table.setModel(ItemModel(20, 4))
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

        #self.expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
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

        item1 = QtWidgets.QTableWidgetItem('Сумма')
        item1.setBackground(QtGui.QColor(205, 175, 149))
        self.budget_table.setHorizontalHeaderItem(0, item1)

        item2 = QtWidgets.QTableWidgetItem('Бюджет')
        item2.setBackground(QtGui.QColor(205, 175, 149))
        self.budget_table.setHorizontalHeaderItem(1, item2)

        self.budget_table.setStyleSheet('border: 1px solid gray; border-radius: 5px;')

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

    def open_editor(self):
        self.editor.set_parent_window(self)
        self.editor.set_category_list(self.categories)
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
