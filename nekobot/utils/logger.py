"""
日志系统模块
"""

import logging
import asyncio
from typing import List, Optional, Set
from datetime import datetime
import colorlog
from collections import deque


class LogHandler(logging.Handler):
    """自定义日志处理器，支持 WebSocket 实时推送"""

    def __init__(self):
        super().__init__()
        self.websocket_clients: Set = set()
        self.log_history = deque(maxlen=1000)

    def emit(self, record):
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "line": record.lineno,
            }
            self.log_history.append(log_data)

            # 异步推送到所有 WebSocket 客户端
            if self.websocket_clients:
                asyncio.create_task(self._broadcast(log_data))
        except Exception:
            self.handleError(record)

    async def _broadcast(self, log_data):
        """广播日志到所有连接的客户端"""
        disconnected = set()
        for ws in self.websocket_clients:
            try:
                await ws.send_json(log_data)
            except Exception:
                disconnected.add(ws)

        self.websocket_clients -= disconnected

    def add_client(self, websocket):
        """添加 WebSocket 客户端"""
        self.websocket_clients.add(websocket)

    def remove_client(self, websocket):
        """移除 WebSocket 客户端"""
        self.websocket_clients.discard(websocket)

    def get_history(self, limit: Optional[int] = None) -> List:
        """获取历史日志"""
        if limit:
            return list(self.log_history)[-limit:]
        return list(self.log_history)


log_handler = LogHandler()


def setup_logger(name: str = "nekobot", level: str = "INFO") -> logging.Logger:
    """配置日志系统"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    if logger.handlers:
        return logger

    # 控制台处理器（带颜色）
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 添加自定义日志处理器
    log_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    )
    logger.addHandler(log_handler)

    return logger


def get_logger(name: str = "nekobot") -> logging.Logger:
    """获取日志实例"""
    return logging.getLogger(name)

