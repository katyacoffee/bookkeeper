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
