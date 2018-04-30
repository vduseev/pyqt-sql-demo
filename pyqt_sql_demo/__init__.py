import sys

from PyQt5.QtWidgets import QApplication

from pyqt_sql_demo.main_window import MainWindow


app = None
APP_NAME = 'PyQt SQL Demo'


def main():
    global app
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    w = MainWindow()
    w.setWindowTitle(APP_NAME)
    w.show()

    app.exec()

