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
import sys

def get_assets(asset_path: str) -> str:
    """
    获取资源文件的绝对路径，兼容开发环境和打包后的环境

    Args:
        asset_path (str): 相对于assets目录的文件路径，如 "images/close.png"

    Returns:
        str: 资源文件的绝对路径
    """

    # 检查是否在Nuitka打包环境中运行
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包环境
        base_path = sys._MEIPASS
    elif getattr(sys, 'frozen', False):
        # Nuitka 打包环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 在开发环境中，使用当前文件所在目录作为基准
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)  # 从utils目录到src目录

    full_path = os.path.join(base_path, asset_path)

    # 验证路径是否存在
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"资源文件未找到: {full_path}")

    return full_path
