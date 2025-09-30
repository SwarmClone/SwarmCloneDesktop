import sys
import os
from PySide6.QtWidgets import QApplication
from windows.main_window import MainWindow

def main():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, app_dir)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()