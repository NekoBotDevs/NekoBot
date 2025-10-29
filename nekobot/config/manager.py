"""
配置管理器 - NekoConfigManager
支持配置动态加载和热重载
"""

import json
import secrets
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, Callable, List
from filelock import FileLock
from watchfiles import awatch

from nekobot.utils.logger import get_logger

logger = get_logger("config")


class NekoConfigManager:
    """配置管理器 - 负责动态加载和管理所有配置"""

    def __init__(self, config_dir: Optional[Path] = None, auto_reload: bool = True):
        if config_dir is None:
            config_dir = Path("./data")

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / "config.json"
        self.lock_file = self.config_dir / "config.lock"

        self._config: Dict[str, Any] = {}
        self._callbacks: List[Callable] = []
        self._watch_task: Optional[asyncio.Task] = None
        self._auto_reload = auto_reload
        self._watch_started = False

        self._load_config()

        # 不在初始化时启动监控，延迟到有事件循环时

    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with FileLock(str(self.lock_file)):
                    with open(self.config_file, "r", encoding="utf-8") as f:
                        self._config = json.load(f)
                logger.info(f"配置文件加载成功: {self.config_file}")
            except Exception as e:
                logger.error(f"配置文件加载失败: {e}")
                self._config = {}
        else:
            self._config = self._get_default_config()
            self._save_config()
            logger.info("使用默认配置并保存")

    def _save_config(self):
        """保存配置文件"""
        try:
            with FileLock(str(self.lock_file)):
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(self._config, f, ensure_ascii=False, indent=2)
            logger.info("配置文件保存成功")
        except Exception as e:
            logger.error(f"配置文件保存失败: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 6285,
                "cors_origins": ["http://127.0.0.1:6285", "http://localhost:6285"],
            },
            "security": {
                "jwt_secret": secrets.token_urlsafe(32),
                "jwt_algorithm": "HS256",
                "jwt_expire_hours": 24,
            },
            "logging": {"level": "INFO", "max_history": 1000},
            "bot": {
                "command_prefix": "/",
                "admin_users": [],
            },
            "github_proxy": {
                "proxies": [
                    "https://ghproxy.com",
                    "https://edgeone.gh-proxy.com",
                    "https://hk.gh-proxy.com",
                    "https://gh.llkk.cc",
                    "direct",
                ],
                "selected": "direct",
            },
            "pip_mirror": {
                "mirrors": [
                    "https://pypi.tuna.tsinghua.edu.cn/simple",
                    "https://pypi.mirrors.ustc.edu.cn/simple",
                    "https://pypi.mirrors.aliyun.com/simple",
                    "https://pypi.org/simple",
                ],
                "selected": "https://pypi.org/simple",
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点号分隔的嵌套键）"""
        # 首次访问时启动监控（如果启用了自动重载）
        if self._auto_reload and not self._watch_started:
            self.start_watching()

        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any, save: bool = True):
        """设置配置值（支持点号分隔的嵌套键）"""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

        if save:
            self._save_config()

        logger.info(f"配置已更新: {key} = {value}")

    def delete(self, key: str, save: bool = True):
        """删除配置项"""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                return
            config = config[k]

        if keys[-1] in config:
            del config[keys[-1]]
            if save:
                self._save_config()
            logger.info(f"配置已删除: {key}")

    def reload(self):
        """重新加载配置"""
        old_config = self._config.copy()
        self._load_config()

        # 检查配置是否有变化
        if old_config != self._config:
            logger.info("配置已重新加载，检测到变更")
            self._notify_callbacks(old_config, self._config)
        else:
            logger.info("配置已重新加载，无变更")

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()

    def update(self, config: Dict[str, Any], save: bool = True):
        """更新配置（合并）"""
        self._config.update(config)
        if save:
            self._save_config()
        logger.info("配置已批量更新")

    def reset_to_default(self):
        """重置为默认配置"""
        old_config = self._config.copy()
        self._config = self._get_default_config()
        self._save_config()
        logger.warning("配置已重置为默认值")
        self._notify_callbacks(old_config, self._config)

    def on_config_change(self, callback: Callable):
        """
        注册配置变更回调函数

        Args:
            callback: 回调函数，接收 (old_config, new_config) 参数
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
            logger.info(f"已注册配置变更回调: {callback.__name__}")

    def remove_callback(self, callback: Callable):
        """移除配置变更回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            logger.info(f"已移除配置变更回调: {callback.__name__}")

    def _notify_callbacks(self, old_config: Dict, new_config: Dict):
        """通知所有回调函数"""
        for callback in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(old_config, new_config))
                else:
                    callback(old_config, new_config)
                logger.debug(f"已通知回调: {callback.__name__}")
            except Exception as e:
                logger.error(f"回调执行失败 {callback.__name__}: {e}")

    def start_watching(self):
        """启动配置文件监控"""
        if self._watch_started:
            return

        try:
            # 检查是否有运行中的事件循环
            asyncio.get_running_loop()
            if self._watch_task is None or self._watch_task.done():
                self._watch_task = asyncio.create_task(self._watch_config_file())
                self._watch_started = True
                logger.info(f"配置文件监控已启动: {self.config_file}")
        except RuntimeError:
            # 没有运行中的事件循环，延迟启动
            logger.debug("事件循环未运行，配置文件监控将在首次访问时启动")

    def stop_watching(self):
        """停止配置文件监控"""
        if self._watch_task and not self._watch_task.done():
            self._watch_task.cancel()
            self._watch_started = False
            logger.info("配置文件监控已停止")

    async def _watch_config_file(self):
        """监控配置文件变化"""
        try:
            async for changes in awatch(str(self.config_file)):
                logger.info(f"检测到配置文件变化: {changes}")
                # 延迟一小段时间，避免文件写入未完成
                await asyncio.sleep(0.1)
                self.reload()
        except asyncio.CancelledError:
            logger.info("配置文件监控已取消")
        except Exception as e:
            logger.error(f"配置文件监控异常: {e}")


# 全局配置管理器实例
_config_manager: Optional[NekoConfigManager] = None


def get_config_manager() -> NekoConfigManager:
    """获取配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = NekoConfigManager()
    return _config_manager

