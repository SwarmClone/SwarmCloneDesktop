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

from typing import Any

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot

class BaseView(QWidget):
    """Base class for all views"""

    def __init__(self, state_manager, data_manager, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self.data_manager = data_manager
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Subclasses must implement this method"""
        raise NotImplementedError

    def connect_signals(self):
        self.state_manager.state_changed.connect(self.on_state_changed)
        self.data_manager.data_loaded.connect(self.on_data_loaded)

    @Slot(str, object)
    def on_state_changed(self, key: str, value: Any):
        """Handle state changes"""
        pass

    @Slot(dict)
    def on_data_loaded(self, data_dict: dict):
        """Handle data loading completion"""
        pass
