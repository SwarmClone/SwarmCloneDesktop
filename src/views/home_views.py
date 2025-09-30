from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from .base_view import BaseView


class HomeView(BaseView):
    def __init__(self, state_manager, data_manager):
        super().__init__(state_manager, data_manager)
        self.state_manager = state_manager
        self.data_manager = data_manager
        self.setup_ui()

        self.title_label = None

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.title_label = QLabel("Home View")

        self.settings_button = QPushButton("进入设置")
        self.settings_button.clicked.connect(self.go_to_settings)
        layout.addWidget(self.settings_button)

        layout.addWidget(self.title_label)

    def go_to_settings(self):
        self.state_manager.set('current_view', 'settings')

