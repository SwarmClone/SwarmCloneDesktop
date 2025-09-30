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