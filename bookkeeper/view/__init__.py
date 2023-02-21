from dataclasses import dataclass
import sys

from PySide6 import QtCore, QtGui, QtWidgets  # последний - виджет, содержащий все необходимые документы


@dataclass
class AddExpenseItem:
    category: int
    comment: str
    amount: float


# from PySide6.QtWidgets import
class AddExpense(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.layout = QtWidgets.QHBoxLayout()  # создаем расладку, чтобы поместить в один виджет несколько
        # self.setLayout(self.layout)  # заполнение виджета раскладкой

        self.grid = QtWidgets.QGridLayout()

        self.comment = 'TODO: сделать добавление комментария?'

        sum_text_widget = QtWidgets.QLabel("Сумма")
        self.grid.addWidget(sum_text_widget, 1, 1)

        cat_text_widget = QtWidgets.QLabel("Категория")
        self.grid.addWidget(cat_text_widget, 2, 1)

        self.sum_widget = QtWidgets.QLineEdit('0')
        self.sum_widget.setValidator(QtGui.QIntValidator(1, 10000000, self))
        self.grid.addWidget(self.sum_widget, 1, 2)

        self.cat_list_widget = ListWidget()
        self.grid.addWidget(self.cat_list_widget, 2, 2)

        self.btn = QtWidgets.QPushButton('Редактировать')
        self.grid.addWidget(self.btn, 2, 3)
        self.btn.clicked.connect(self.get_data)

        self.btn = QtWidgets.QPushButton('Добавить')
        self.grid.addWidget(self.btn, 3, 2)
        self.btn.clicked.connect(self.get_data)

        self.setLayout(self.grid)

        # self.amount = QtWidgets.QLineEdit()  # LineEdit позволяет в отличие от TextEdit в одну строчку только набирать
        # self.amount.setPlaceholderText('Сумма')
        # self.amount.setValidator(QtGui.QIntValidator(1, 10000000, self))  # проверяет правильность введенных данных
        # self.layout.addWidget(self.amount)

    def is_filled(self):
        return bool(self.cat_list_widget.get_id() and self.comment and self.sum_widget.text())

    def get_data(self):
        item = AddExpenseItem(self.cat_list_widget.get_id(), self.comment, int(self.sum_widget.text()))
        print(item)  # TODO: здесь будет соединение с базой
        return item


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
        self.add_line()
        self.add_line('Хозтовары')
        self.add_line('Автотовары')
        self.add_line('Лекарства')
        self.add_line('Книги')
        self.add_line('Одежда')
        self.add_line('Украшения')
        self.lines = sorted(self.lines)

        for line in self.lines:
            self.addItem(line)

    def add_line(self, name: str = 'Продукты', parent: int = 0):
        AddCat(name, parent)
        self.lines.append(name)

    def changeEvent(self, event):
        if all(line != '' for line in self.lines):
            self.add_line()

    def get_data(self):
        return [line.get_data() for line in self.lines]

    def get_id(self) -> int:
        print(self.currentText())
        return 1 # TODO: сделать вывод id категории из таблицы категорий по self.text()


class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500) # TODO: подобрать размер относительно габаритов экрана

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
        # self.budget_adder = AddExpense()

        self.layout.addWidget(self.expense_adder)
        # self.layout.addWidget(self.budget_adder)

    def set_data(self, data: list[list[str]]):
        for i, row in enumerate(data):
            for j, x in enumerate(row):
                self.expenses_table.setItem(i, j, QtWidgets.QTableWidgetItem(x.capitalize()))


 # app = QtWidgets.QApplication(sys.argv)  # при создании приложения передаются в него аргументы командной строки и само название приложения

app = QtWidgets.QApplication(sys.argv)  # передаем аргументы командной строки
window = MainWindow()
window.show()
app.exec()