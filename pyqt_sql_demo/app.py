import sys
from PyQt5.QtWidgets import QApplication
from pyqt_sql_demo.widgets.main import MainWindow


app = None
APP_NAME = "PyQt SQL Demo"


def launch():
    global app
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    w = MainWindow()
    w.setWindowTitle(APP_NAME)
    w.show()

    app.exec()


if __name__ == "__main__":
    launch()
