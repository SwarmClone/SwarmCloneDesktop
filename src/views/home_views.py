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
import os
import signal

from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from .base_view import BaseView


def test_crash():
    import ctypes
    ctypes.string_at(0)
    os.kill(os.getpid(), signal.SIGTERM)


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

        self.test_button = QPushButton("发起测试崩溃")
        self.test_button.clicked.connect(test_crash)
        layout.addWidget(self.test_button)

        layout.addWidget(self.title_label)

    def go_to_settings(self):
        self.state_manager.set('current_view', 'settings')

