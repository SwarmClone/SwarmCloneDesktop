# SwarmClone Desktop
#
# Copyright (C) 2025 SwarmClone <https://github.com/SwarmClone> and contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Eclipse Public License, Version 2.0 (EPL-2.0),
# as published by the Eclipse Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Eclipse Public License 2.0 for more details.
#
# You should have received a copy of the Eclipse Public License 2.0
# along with this program.  For the full text of the Eclipse Public License 2.0,
# see <https://www.eclipse.org/legal/epl-2.0/>.
from PySide6.QtCore import QObject
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout

from views.home_views import HomeView
from views.settings_views import SettingsView
from models.app_state import StateManager
from models.data_manager import DataManager
from models.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SwarmClone Desktop")
        self.setGeometry(100, 100, 1100, 650)

        self.state_manager = StateManager()
        self.data_manager = DataManager(self.state_manager)
        self.theme_manager = ThemeManager()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.view_stack = QStackedWidget()

        self.views = {}
        self.create_views()

        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.view_stack)
        layout.setContentsMargins(0, 0, 0, 0)

        self.state_manager.state_changed.connect(self.on_state_changed)
        self.theme_manager.themeChanged.connect(self.apply_theme)

        # Apply theme after showing the initial view
        self.switch_view("home")
        self.apply_theme(self.theme_manager.current_theme)

    def create_views(self):
        self.views["home"] = HomeView(self.state_manager, self.data_manager)
        self.views["settings"] = SettingsView(self.state_manager, self.data_manager)

        for view in self.views.values():
            self.view_stack.addWidget(view)

    def switch_view(self, view_name: str):
        if view_name in self.views:
            index = list(self.views.keys()).index(view_name)
            self.view_stack.setCurrentIndex(index)

    def on_state_changed(self, key: str, value):
        if key == "current_view":
            self.switch_view(value)

    def apply_theme(self, theme_name: str):
        theme = self.theme_manager.get_theme(theme_name)

        palette = self.palette()

        palette.setColor(QPalette.Window, QColor(theme["background"]))
        palette.setColor(QPalette.Base, QColor(theme["foreground"]))
        palette.setColor(QPalette.WindowText, QColor(theme["text"]))
        palette.setColor(QPalette.Text, QColor(theme["text"]))
        palette.setColor(QPalette.Button, QColor(theme["button_background"]))
        palette.setColor(QPalette.ButtonText, QColor(theme["button_text"]))
        palette.setColor(QPalette.Mid, QColor(theme["border"]))

        self.setPalette(palette)

        stylesheet = f"""
            QMainWindow {{
                background-color: {theme["background"]};
            }}
            
            QWidget {{
                color: {theme["text"]};
                background-color: {theme["background"]};
            }}
            
            QPushButton {{
                background-color: {theme["button_background"]};
                color: {theme["button_text"]};
                border: 1px solid {theme["border"]};
                padding: 6px;
                border-radius: 4px;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {theme["button_hover"]};
            }}
            
            QPushButton:pressed {{
                background-color: {theme["button_hover"]};
            }}
            
            QLabel {{
                color: {theme["text"]};
            }}
        """

        self.setStyleSheet(stylesheet)

        # Update all child widgets
        self.update_styles_recursive(self)

    def update_styles_recursive(self, widget):
        if isinstance(widget, QObject) and hasattr(widget, 'style'):
            try:
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update(widget.rect())
            except Exception:
                # Skip update if an error occurs
                pass

        # Recursively update child widgets
        for child in widget.children():
            if isinstance(child, QObject):
                self.update_styles_recursive(child)
