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

from PySide6.QtCore import QObject, Signal, QThread, QTimer
import pandas as pd


class DataManager(QObject):
    data_loaded = Signal(dict)
    data_updated = Signal(str, object)  # table_name, data

    def __init__(self, state_manager):
        super().__init__()
        self.state_manager = state_manager
        self._data_tables = {}

    def load_data(self, table_name: str, file_path: str):
        def load_task():
            try:
                data = pd.read_csv(file_path)
                self._data_tables[table_name] = data
                self.data_loaded.emit({table_name: data})
                self.state_manager.set('is_loading', False)
            except Exception as e:
                print(f"Error loading data: {e}")

        # async loading
        self.state_manager.set('is_loading', True)
        QTimer.singleShot(0, load_task)

    def get_table(self, table_name: str) -> pd.DataFrame:
        return self._data_tables.get(table_name)