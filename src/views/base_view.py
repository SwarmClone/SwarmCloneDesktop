from typing import Any

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot


class BaseView(QWidget):
    """所有视图的基类"""

    def __init__(self, state_manager, data_manager, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self.data_manager = data_manager
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """子类必须实现此方法"""
        raise NotImplementedError

    def connect_signals(self):
        self.state_manager.state_changed.connect(self.on_state_changed)
        self.data_manager.data_loaded.connect(self.on_data_loaded)

    @Slot(str, object)
    def on_state_changed(self, key: str, value: Any):
        """处理状态变化"""
        pass

    @Slot(dict)
    def on_data_loaded(self, data_dict: dict):
        """处理数据加载完成"""
        pass