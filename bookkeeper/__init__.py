import sys

from PySide6 import QtWidgets

from bookkeeper.view import View
from bookkeeper.view.bookkeeper import Bookkeeper

if not QtWidgets.QApplication.instance():
    app = QtWidgets.QApplication(sys.argv)
else:
    app = QtWidgets.QApplication.instance()
view = View()
bk = Bookkeeper(view)
view.set_bookkeeper(bk)
view.show()
app.exec()
exit()
