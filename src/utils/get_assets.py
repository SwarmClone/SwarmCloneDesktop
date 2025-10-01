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
    Get the absolute path of resource files,
    compatible with development and packaged environments

    Args:
        asset_path (str): File path relative to
                        the assets directory, e.g. "images/close.png"

    Returns:
        str: Absolute path of the resource file
    """

    # Check if running in Nuitka packaging environment
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller packaging environment
        base_path = sys._MEIPASS
    elif getattr(sys, 'frozen', False):
        # Nuitka packaging environment
        base_path = os.path.dirname(sys.executable)
    else:
        # In development environment, use the current file's directory as the base
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)  # From utils directory to src directory

    full_path = os.path.join(base_path, asset_path)

    # Verify that the path exists
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource file not found: {full_path}")

    return full_path
