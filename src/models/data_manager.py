# app/models/data_manager.py
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

        # 异步加载
        self.state_manager.set('is_loading', True)
        QTimer.singleShot(0, load_task)

    def get_table(self, table_name: str) -> pd.DataFrame:
        return self._data_tables.get(table_name)