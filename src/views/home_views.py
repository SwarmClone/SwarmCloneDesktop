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

from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox
from .base_view import BaseView

def test_crash():
    import ctypes
    try:
        ctypes.memmove(0, 0x1000, 8)
    except:
        pass

    invalid_ptr = ctypes.cast(0x5C, ctypes.POINTER(ctypes.c_int))
    invalid_ptr.contents.value = 42
    def overflow():
        return overflow()

    overflow()

class HomeView(BaseView):
    def __init__(self, state_manager, data_manager):
        super().__init__(state_manager, data_manager)
        self.test_button = None
        self.settings_button = None
        self.theme_combo = None
        self.state_manager = state_manager
        self.data_manager = data_manager
        self.setup_ui()
        self.title_label = None

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.title_label = QLabel("Home View")

        button_layout = QHBoxLayout()

        self.settings_button = QPushButton("进入设置")
        self.settings_button.clicked.connect(self.go_to_settings)
        button_layout.addWidget(self.settings_button)

        self.test_button = QPushButton("发起测试崩溃")
        self.test_button.clicked.connect(test_crash)
        button_layout.addWidget(self.test_button)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("跟随系统", "default")
        self.theme_combo.addItem("浅色主题", "light")
        self.theme_combo.addItem("深色主题", "dark")
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        button_layout.addWidget(self.theme_combo)

        layout.addLayout(button_layout)
        layout.addWidget(self.title_label)

        # 初始化下拉框选中项
        self.init_theme_combo()

    def init_theme_combo(self):
        """初始化主题下拉框选中项"""
        main_window = self.window()
        if hasattr(main_window, 'theme_manager'):
            current_theme = main_window.theme_manager.current_theme
            index = self.theme_combo.findData(current_theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

    def go_to_settings(self):
        self.state_manager.set('current_view', 'settings')

    def on_theme_changed(self, index):
        """主题选择改变时的处理函数"""
        theme_id = self.theme_combo.itemData(index)
        # 获取主窗口并应用主题
        main_window = self.window()
        if hasattr(main_window, 'theme_manager'):
            main_window.theme_manager.set_theme(theme_id)
