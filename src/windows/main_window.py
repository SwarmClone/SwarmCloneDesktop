# app/main_window.py
from typing import Any

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget
from PySide6.QtCore import Slot

from views import HomeView, SettingsView
from models.app_state import StateManager
from models.data_manager import DataManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings_view = None
        self.home_view = None
        self.view_stack = None
        self.central_widget = None
        self.state_manager = StateManager()
        self.data_manager = DataManager(self.state_manager)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.setWindowTitle("SwarmClone Desktop")
        self.setGeometry(100, 100, 1100, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        self.view_stack = QStackedWidget()
        layout.addWidget(self.view_stack)

        self.home_view = HomeView(self.state_manager, self.data_manager)
        self.settings_view = SettingsView(self.state_manager, self.data_manager)

        self.view_stack.addWidget(self.home_view)
        self.view_stack.addWidget(self.settings_view)

    def connect_signals(self):
        # 连接状态变化信号
        self.state_manager.state_changed.connect(self.on_state_changed)

    @Slot(str, object)
    def on_state_changed(self, key: str, value: Any):
        if key == 'current_view':
            self.switch_view(value)

    def switch_view(self, view_name: str):
        view_map = {
            'home': 0,
            'settings': 1
        }
        index = view_map.get(view_name, 0)
        self.view_stack.setCurrentIndex(index)
