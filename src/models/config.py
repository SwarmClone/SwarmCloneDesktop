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
            # 同步初始数据到 dict
            cls._instance.update(cls._instance._worker.data)
        return cls._instance

    # 如果涉及用户外部修改配置文件，需要调用这个函数
    # 虽然目前来说不太可能...
    def reload(self):
        self._worker.load()

    # 立即保存
    # 这个函数在一些需要频繁修改配置的场景或许有用
    def save(self):
        self._worker.dump()

    # 程序退出前必须调用以确保所有数据都被保存
    def cleanup(self) -> None:
        self._worker.prepare_shutdown()
        self._worker.dump()

    def set_default(self, key: str, default: Any) -> Any:
        if key not in self:
            self[key] = default
        return self[key]

    # 支持通过 cfg['key'] = value 赋值
    def __setitem__(self, key: str, value: Any) -> None:
        self._worker.data[key] = value
        self._worker.trigger_save()

    # 支持通过 cfg['key'] 访问
    def __getitem__(self, key):
        return self._worker.data[key]

    # 建议使用这个，因为如果键值不存在就不需要再写 if else 来替换为默认值
    # 或者也可以提前使用 set_default 来设置默认值
    def get(self, key, default=None):
        return self._worker.data.get(key, default)


cfg: _Config = _Config()