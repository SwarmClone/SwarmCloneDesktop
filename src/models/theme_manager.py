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
from typing import Dict, Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication


class ThemeManager(QObject):
    themeChanged = Signal(str)  # 发送主题名称

    def __init__(self):
        super().__init__()
        self._current_theme = "default"
        self._themes = {
            "default": {
                "primary_color": "#2196F3",
                "background": "#F5F5F5",
                "foreground": "#FFFFFF",
                "text": "#212121",
                "button_text": "#FFFFFF",
                "button_background": "#1772F6",
                "button_hover": "#1976D2",
                "border": "#BDBDBD"
            },
            "dark": {
                "primary_color": "#2196F3",
                "background": "#1B1A19",
                "foreground": "#424242",
                "text": "#FFFFFF",
                "button_text": "#FFFFFF",
                "button_background": "#2579BE",
                "button_hover": "#1976D2",
                "border": "#757575"
            },
            "light": {
                "primary_color": "#2196F3",
                "background": "#FAFAFA",
                "foreground": "#FFFFFF",
                "text": "#212121",
                "button_text": "#FFFFFF",
                "button_background": "#0078D4",
                "button_hover": "#1976D2",
                "border": "#E0E0E0"
            }
        }

    @property
    def current_theme(self) -> str:
        return self._current_theme

    @property
    def themes(self) -> Dict[str, Any]:
        return self._themes

    def get_theme(self, theme_name: str) -> Dict[str, str]:
        # 如果是默认主题，根据系统主题决定实际使用的主题
        if theme_name == "default":
            return self.get_system_theme()
        return self._themes.get(theme_name, self._themes["dark"])

    def get_system_theme(self) -> Dict[str, str]:
        """根据系统设置获取主题"""
        try:
            # 检查系统主题设置
            palette = QApplication.palette()
            window_color = palette.color(QPalette.Window)

            # 如果窗口背景较暗，则使用深色主题
            if window_color.lightness() < 128:
                return self._themes["dark"]
            else:
                return self._themes["light"]
        except:
            # 出错时默认使用深色主题
            return self._themes["dark"]

    def set_theme(self, theme_name: str):
        if theme_name in self._themes or theme_name == "default":
            self._current_theme = theme_name
            self.themeChanged.emit(theme_name)
