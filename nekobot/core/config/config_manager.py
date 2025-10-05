"""配置管理器"""
import json
import os
from pathlib import Path
from typing import Any, Optional
from filelock import FileLock
import pyjson5


class NekoConfigManager:
    """配置管理器,负责加载、保存和动态更新配置"""

    def __init__(self, config_dir: str = "./data"):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config_cache = {}
        self._lock_dir = self.config_dir / "locks"
        self._lock_dir.mkdir(parents=True, exist_ok=True)

    def _get_lock_path(self, config_file: str) -> Path:
        """获取配置文件的锁文件路径"""
        return self._lock_dir / f"{config_file}.lock"

    def load_config(
        self, config_file: str, default: Optional[dict] = None
    ) -> dict:
        """加载配置文件
        
        Args:
            config_file: 配置文件名
            default: 默认配置
            
        Returns:
            配置字典
        """
        config_path = self.config_dir / config_file
        lock_path = self._get_lock_path(config_file)

        if config_file in self._config_cache:
            return self._config_cache[config_file]

        if not config_path.exists():
            if default is not None:
                self.save_config(config_file, default)
                return default
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_file.endswith(".json5"):
                    config = pyjson5.load(f)
                else:
                    config = json.load(f)
            self._config_cache[config_file] = config
            return config
        except Exception as e:
            raise RuntimeError(
                f"加载配置文件 {config_file} 失败: {e}"
            )

    def save_config(self, config_file: str, config: dict) -> None:
        """保存配置文件
        
        Args:
            config_file: 配置文件名
            config: 配置字典
        """
        config_path = self.config_dir / config_file
        lock_path = self._get_lock_path(config_file)

        with FileLock(lock_path, timeout=10):
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self._config_cache[config_file] = config
            except Exception as e:
                raise RuntimeError(
                    f"保存配置文件 {config_file} 失败: {e}"
                )

    def update_config(
        self, config_file: str, key: str, value: Any
    ) -> None:
        """更新配置项
        
        Args:
            config_file: 配置文件名
            key: 配置键
            value: 配置值
        """
        config = self.load_config(config_file, {})
        keys = key.split(".")
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.save_config(config_file, config)

    def get_config(
        self, config_file: str, key: str, default: Any = None
    ) -> Any:
        """获取配置项
        
        Args:
            config_file: 配置文件名
            key: 配置键(支持点号分隔的嵌套键)
            default: 默认值
            
        Returns:
            配置值
        """
        config = self.load_config(config_file, {})
        keys = key.split(".")
        current = config

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def delete_config(self, config_file: str, key: str) -> None:
        """删除配置项
        
        Args:
            config_file: 配置文件名
            key: 配置键
        """
        config = self.load_config(config_file, {})
        keys = key.split(".")
        current = config

        for k in keys[:-1]:
            if k not in current:
                return
            current = current[k]

        if keys[-1] in current:
            del current[keys[-1]]
            self.save_config(config_file, config)

    def clear_cache(self, config_file: Optional[str] = None) -> None:
        """清除配置缓存
        
        Args:
            config_file: 配置文件名,为None时清除所有缓存
        """
        if config_file:
            self._config_cache.pop(config_file, None)
        else:
            self._config_cache.clear()