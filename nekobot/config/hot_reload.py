"""
配置热重载管理器
"""

from typing import Dict, Any
from nekobot.config.manager import get_config_manager
from nekobot.utils.logger import get_logger

logger = get_logger("hot_reload")


class ConfigHotReloadManager:
    """配置热重载管理器"""

    def __init__(self):
        self.config_manager = get_config_manager()
        self._setup_callbacks()

    def _setup_callbacks(self):
        """设置配置变更回调"""
        self.config_manager.on_config_change(self.on_server_config_change)
        self.config_manager.on_config_change(self.on_logging_config_change)
        self.config_manager.on_config_change(self.on_bot_config_change)

    async def on_server_config_change(
        self, old_config: Dict[str, Any], new_config: Dict[str, Any]
    ):
        """服务器配置变更处理"""
        old_server = old_config.get("server", {})
        new_server = new_config.get("server", {})

        if old_server != new_server:
            logger.warning("服务器配置已变更，部分配置需要重启服务才能生效")

            if old_server.get("port") != new_server.get("port"):
                logger.warning(
                    f"端口已变更: {old_server.get('port')} -> {new_server.get('port')}"
                )

            if old_server.get("cors_origins") != new_server.get("cors_origins"):
                logger.info(
                    f"CORS 配置已变更: {old_server.get('cors_origins')} -> {new_server.get('cors_origins')}"
                )

    async def on_logging_config_change(
        self, old_config: Dict[str, Any], new_config: Dict[str, Any]
    ):
        """日志配置变更处理"""
        old_logging = old_config.get("logging", {})
        new_logging = new_config.get("logging", {})

        if old_logging != new_logging:
            logger.info("日志配置已变更")

            if old_logging.get("level") != new_logging.get("level"):
                new_level = new_logging.get("level", "INFO")
                logger.info(f"日志级别已变更为: {new_level}")

                # 动态更新日志级别
                import logging

                logging.getLogger("nekobot").setLevel(
                    getattr(logging, new_level.upper())
                )

    async def on_bot_config_change(
        self, old_config: Dict[str, Any], new_config: Dict[str, Any]
    ):
        """机器人配置变更处理"""
        old_bot = old_config.get("bot", {})
        new_bot = new_config.get("bot", {})

        if old_bot != new_bot:
            logger.info("机器人配置已变更")

            if old_bot.get("command_prefix") != new_bot.get("command_prefix"):
                logger.info(
                    f"命令前缀已变更: {old_bot.get('command_prefix')} -> {new_bot.get('command_prefix')}"
                )

            if old_bot.get("admin_users") != new_bot.get("admin_users"):
                logger.info(f"管理员列表已变更: {new_bot.get('admin_users')}")


# 全局热重载管理器
_hot_reload_manager = None


def get_hot_reload_manager() -> ConfigHotReloadManager:
    """获取热重载管理器实例"""
    global _hot_reload_manager
    if _hot_reload_manager is None:
        _hot_reload_manager = ConfigHotReloadManager()
    return _hot_reload_manager

