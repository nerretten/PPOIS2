import sys
from PySide6.QtWidgets import QApplication

from controller import Controller
from view.main_window import MainWindow
from models import StudentModel, Student


def main():
    app = QApplication(sys.argv)
    model = StudentModel()
    view = MainWindow()
    controller = Controller(model, view)
    view.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()