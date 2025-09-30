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

from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from typing import Any


@dataclass
class AppState:
    is_loading: bool = False
    current_view: str = "home"
    data_cache: dict = None


class StateManager(QObject):
    """程序状态管理器"""
    state_changed = Signal(str, object)  # key, value

    def __init__(self):
        super().__init__()
        self._state = AppState()
        self._state.data_cache = {}

    def get(self, key: str) -> Any:
        return getattr(self._state, key)

    def set(self, key: str, value: Any):
        old_value = getattr(self._state, key)
        if old_value != value:
            setattr(self._state, key, value)
            self.state_changed.emit(key, value)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.set(key, value)