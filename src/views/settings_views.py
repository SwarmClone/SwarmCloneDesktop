from PySide6.QtWidgets import QVBoxLayout,QLabel
from .base_view import BaseView


# 在 SettingsView 类中添加按钮
from PySide6.QtWidgets import QPushButton

class SettingsView(BaseView):
    def __init__(self, state_manager, data_manager):
        super().__init__(state_manager, data_manager)
        self.state_manager = state_manager
        self.data_manager = data_manager

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.home_button = QPushButton("返回主页")
        self.home_button.clicked.connect(self.go_to_home)
        layout.addWidget(self.home_button)


    def go_to_home(self):
        self.state_manager.set('current_view', 'home')

