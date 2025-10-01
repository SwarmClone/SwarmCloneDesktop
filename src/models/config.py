#file:E:\Code\Python\SwarmCloneDesktop\src\models\config.py
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

import json, os
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, QTimer, QMutex, QMutexLocker


_JSON_PATH = Path.home() / ".swarmclone" / "config.json"
_DEBOUNCE_MS = 300


class ConfigWorker(QObject):
    def __init__(self, json_path):
        super().__init__()
        self.json_path = json_path
        self.data = {}
        self.mutex = QMutex()
        self.shutting_down = False
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.dump)

    def _ensure_file(self):
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.json_path.exists():
            self.json_path.write_text("{}", encoding="utf-8")

    def load(self):
        with QMutexLocker(self.mutex):
            self._ensure_file()
            try:
                with self.json_path.open("r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}

    def dump(self):
        with QMutexLocker(self.mutex):
            if self.shutting_down:
                return
            try:
                with self.json_path.open("w", encoding="utf-8") as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
            except Exception:
                pass

    def trigger_save(self):
        if not self.shutting_down:
            self.save_timer.stop()
            self.save_timer.start(_DEBOUNCE_MS)

    def prepare_shutdown(self):
        with QMutexLocker(self.mutex):
            self.shutting_down = True
            self.save_timer.stop()


class _Config(Dict[str, Any]):
    _instance: Optional["_Config"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)    # type: ignore
            cls._instance._worker = ConfigWorker(_JSON_PATH)
            # Synchronize initial data to dict
            cls._instance.update(cls._instance._worker.data)
        return cls._instance

    # Call this function if the configuration file is modified externally by the user
    # Although this is unlikely at the moment...
    def reload(self):
        self._worker.load()

    # Save immediately
    # This function might be useful in scenarios where configuration changes frequently
    def save(self):
        self._worker.dump()

    # Must be called before program exits to ensure all data is saved
    def cleanup(self) -> None:
        self._worker.prepare_shutdown()
        self._worker.dump()

    def set_default(self, key: str, default: Any) -> Any:
        if key not in self:
            self[key] = default
        return self[key]

    # Supports assignment via cfg['key'] = value
    def __setitem__(self, key: str, value: Any) -> None:
        self._worker.data[key] = value
        self._worker.trigger_save()

    # Supports access via cfg['key']
    def __getitem__(self, key):
        return self._worker.data[key]

    # Recommended to use this, as there's no need to write if-else statements to replace with default values if the key doesn't exist
    # Or you can also use set_default in advance to set default values
    def get(self, key, default=None):
        return self._worker.data.get(key, default)


cfg: _Config = _Config()
