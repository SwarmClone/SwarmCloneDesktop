from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget, QPushButton

class Live2dWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("SwarmClone Live2d Window")

        self.setGeometry(100, 100, 1000, 600)

    # @Slot(str, object)
    # def on_state_changed(self, key: str, value: Any):
    #     if key == 'current_view':
    #         self.switch_view(value)
    #     elif key == 'is_loading':
    #         self.update_loading_state(value)
    #
    # def switch_view(self, view_name: str):
    #     view_map = {
    #         'home': 0,
    #         'settings': 1
    #     }
    #     index = view_map.get(view_name, 0)
    #     self.view_stack.setCurrentIndex(index)