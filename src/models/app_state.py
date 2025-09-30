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