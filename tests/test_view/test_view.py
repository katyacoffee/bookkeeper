from PySide6.QtWidgets import QMessageBox
from _pytest.monkeypatch import monkeypatch
from pytestqt.qt_compat import qt_api
import pytest

from bookkeeper import Bookkeeper
from bookkeeper.view import View

# TODO: добавить тесты для:
# EditorWindow -> btn_add1, btn_del_bud,
#                 btn_add_bud, btn_del_cat
# MainWindow   -> btn_add_comm


@pytest.fixture
def window():
    view = View()
    bk = Bookkeeper(view)
    view.set_bookkeeper(bk)
    bk.del_all_expenses()
    bk.del_all_cats()
    return view.window


def test_addexp(qtbot, window):
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


def test_addcat(qtbot, window):
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


def test_delbud(qtbot, window):
    # constants
    amount = 0

    # prepare
    widget = window.editor
    # widget.sum_widget.setText(f'{amount}')
    # widget.cat_list_widget.setCurrentText(category)

    # test
    qtbot.addWidget(widget)
    qtbot.mouseClick(
        widget.btn_del_bud,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # get results
    bud_value1 = window.budget_table.item(0, 0).text()
    bud_value2 = window.budget_table.item(1, 0).text()
    bud_value3 = window.budget_table.item(2, 0).text()
    assert bud_value1 == f'{amount}'
    assert bud_value2 == f'{amount}'
    assert bud_value3 == f'{amount}'


def test_addbud(qtbot, window):
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


def test_delcat(qtbot, window, monkeypatch):
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


def test_addcomm(qtbot, window):
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
