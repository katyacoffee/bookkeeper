from PySide6.QtWidgets import QMessageBox, QTableWidgetItem
from pytestqt.qt_compat import qt_api
import pytest

from bookkeeper import Bookkeeper, AddExpenseItem
from bookkeeper.view import View


@pytest.fixture
def window():
    view = View()
    bk = Bookkeeper(view)
    view.set_bookkeeper(bk)
    bk.del_all_expenses()
    bk.del_all_cats()
    return view.window


def test_add_exp(qtbot, window):
    # constants
    amount = 123
    category = 'Default'

    # prepare
    widget = window.expense_adder
    widget.sum_widget.setText(f'{amount}')
    window.bk.add_category(category)
    window.update_cat_table()
    widget.cat_list_widget.setCurrentText(category)

    # test
    qtbot.addWidget(widget)
    qtbot.mouseClick(
        widget.btn_add,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # get results
    expense_value = window.expenses_table.item(0, 1).text()
    category_value = window.expenses_table.item(0, 2).text()
    assert expense_value == f'{amount}'
    assert category_value == category


def test_add_cat_no_par(qtbot, window, monkeypatch):
    # constants
    cat = 'Авто'

    # prepare
    widget = window.editor
    widget.set_parent_window(window)
    widget.new1_widget.setText(cat)

    # test
    monkeypatch.setattr(QMessageBox, 'information', lambda *args: QMessageBox.Ok)
    qtbot.addWidget(widget)
    qtbot.mouseClick(
        widget.btn_add1,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # get results
    has_cat = False
    for k in range(0, widget.cat_list_widget.count()):
        if widget.cat_list_widget.itemText(k) == cat:
            has_cat = True
            break
    assert has_cat is True


def test_add_cat_with_par(qtbot, window, monkeypatch):
    # constants
    cat = 'ЖКХ'
    par_cat = 'Квартира'

    # prepare
    widget = window.editor
    widget.set_parent_window(window)
    widget.bk.add_category(par_cat)
    widget.new1_widget.setText(cat)
    widget.new2_widget.setText(par_cat)

    # test
    monkeypatch.setattr(QMessageBox, 'information', lambda *args: QMessageBox.Ok)
    qtbot.addWidget(widget)
    qtbot.mouseClick(
        widget.btn_add1,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # get results
    has_cat = False
    for k in range(0, widget.cat_list_widget.count()):
        if widget.cat_list_widget.itemText(k) == cat:
            has_cat = True
            break
    assert has_cat is True


def test_add_cat_with_unknown_par(qtbot, window, monkeypatch):
    # constants
    cat = 'ЖКХ'
    par_cat = 'Неизвестно'

    # prepare
    widget = window.editor
    widget.set_parent_window(window)
    widget.new1_widget.setText(cat)
    widget.new2_widget.setText(par_cat)

    # test
    monkeypatch.setattr(QMessageBox, 'critical', lambda *args: QMessageBox.Ok)
    qtbot.addWidget(widget)
    qtbot.mouseClick(
        widget.btn_add1,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # get results
    has_cat = False
    for k in range(0, widget.cat_list_widget.count()):
        if widget.cat_list_widget.itemText(k) == cat:
            has_cat = True
            break
    assert has_cat is False


def test_del_bud(qtbot, window, monkeypatch):
    # constants
    amount = 12345
    zero_amount = 0
    cat = 'Default'

    # prepare
    widget = window.editor
    widget.set_parent_window(window)
    window.bk.add_category(cat)
    pk = window.bk.get_cat_id_by_name(cat)
    window.bk.add_expense(AddExpenseItem(pk, '', amount))
    window.update_exp_table()
    window.update_bud_table()

    # test
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.Yes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(
        widget.btn_del_bud,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # get results
    bud_value1 = window.budget_table.item(0, 0).text()
    bud_value2 = window.budget_table.item(1, 0).text()
    bud_value3 = window.budget_table.item(2, 0).text()
    item_date = window.expenses_table.item(0, 0)
    item_amount = window.expenses_table.item(0, 1)
    item_category = window.expenses_table.item(0, 2)
    assert bud_value1 == f'{zero_amount}'
    assert bud_value2 == f'{zero_amount}'
    assert bud_value3 == f'{zero_amount}'
    assert item_date is None or item_date.text() == ''
    assert item_amount is None or item_date.text() == ''
    assert item_category is None or item_date.text() == ''


def test_add_bud(qtbot, window):
    # constants
    amount = 1234
    range_date = 'Неделя'

    # prepare
    widget = window.editor
    widget.set_parent_window(window)
    widget.add_bud_widget.setText(f'{amount}')
    widget.combobox1.setCurrentText(range_date)

    # test
    qtbot.addWidget(widget)
    qtbot.mouseClick(
        widget.btn_add_bud,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # get results
    budget_value1 = window.budget_table.item(0, 1).text()
    budget_value2 = window.budget_table.item(1, 1).text()
    budget_value3 = window.budget_table.item(2, 1).text()
    assert budget_value1 == f'{amount // 7}'
    assert budget_value2 == f'{amount}'
    assert budget_value3 == f'{amount // 7 * 30}'


def test_del_cat(qtbot, window, monkeypatch):
    # constants
    new_cat = 'Медицина'

    # prepare
    widget = window.editor
    widget.set_parent_window(window)
    window.bk.del_cat(new_cat)
    window.bk.add_category(new_cat)
    window.update_cat_table()
    widget.cat_list_widget.setCurrentText(new_cat)

    # test
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, 'information', lambda *args: QMessageBox.Ok)
    qtbot.addWidget(widget)
    qtbot.mouseClick(
        widget.btn_del_cat,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # get results
    has_cat = False
    for k in range(0, widget.cat_list_widget.count()):
        if widget.cat_list_widget.itemText(k) == new_cat:
            has_cat = True
            break
    assert has_cat is False


def test_add_comm(qtbot, window):
    # constants
    comment = 'Конфеты'
    cat = 'Сладости'
    amount = 888

    # prepare
    widget = window.expenses_table
    window.bk.add_category(cat)
    pk = window.bk.get_cat_id_by_name(cat)
    window.bk.add_expense(AddExpenseItem(pk, '', amount))
    window.update_exp_table()
    widget.item(0, 3).setText(comment)

    # test
    qtbot.addWidget(window)
    qtbot.mouseClick(
        window.btn_add_comm,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )
    window.update_exp_table()

    # get results
    comm = window.expenses_table.item(0, 3).text()
    assert comm == comment
