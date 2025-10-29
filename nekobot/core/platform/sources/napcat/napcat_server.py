"""
NapCat WebSocket 服务器
用于接收 NapCat 上报的消息事件
"""

import asyncio
import json
from typing import Optional, Callable
from quart import Quart, websocket as quart_websocket
from nekobot.utils.logger import get_logger
from nekobot.core.platform.sources.napcat.napcat_event import parse_event, EventHandler

logger = get_logger("napcat.server")


class NapCatWebSocketServer:
    """NapCat WebSocket 服务器"""

    def __init__(self, host: str = "0.0.0.0", port: int = 6299, access_token: Optional[str] = None):
        """
        初始化 WebSocket 服务器

        Args:
            host: 监听地址
            port: 监听端口
            access_token: 访问令牌（可选）
        """
        self.host = host
        self.port = port
        self.access_token = access_token
        self.event_handler = EventHandler()

        self.app = Quart(f"napcat_ws_{port}")
        self._setup_routes()

        logger.info(f"NapCat WebSocket 服务器初始化: {host}:{port}")

    def _setup_routes(self):
        """设置路由"""

        @self.app.websocket("/")
        async def ws_handler():
            """WebSocket 连接处理"""
            logger.info("收到 WebSocket 连接请求")

            # 验证 access_token
            if self.access_token:
                auth_header = quart_websocket.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    logger.warning("WebSocket 连接认证失败：缺少 Authorization 头")
                    await quart_websocket.close(1008, "认证失败")
                    return

                token = auth_header[7:]
                if token != self.access_token:
                    logger.warning("WebSocket 连接认证失败：token 不匹配")
                    await quart_websocket.close(1008, "认证失败")
                    return

            logger.info("WebSocket 连接已建立")

            try:
                while True:
                    data = await quart_websocket.receive()

                    try:
                        event_data = json.loads(data)
                        logger.debug(f"收到事件: {event_data.get('post_type')}")

                        # 解析并处理事件
                        event = parse_event(event_data)
                        await self.event_handler.handle_event(event)

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON 解析失败: {e}")
                    except Exception as e:
                        logger.error(f"事件处理失败: {e}", exc_info=True)

            except Exception as e:
                logger.warning(f"WebSocket 连接断开: {e}")

    def on_message(self, func: Callable):
        """注册消息处理器（装饰器）"""
        return self.event_handler.on_message(func)

    def on_notice(self, func: Callable):
        """注册通知处理器（装饰器）"""
        return self.event_handler.on_notice(func)

    def on_request(self, func: Callable):
        """注册请求处理器（装饰器）"""
        return self.event_handler.on_request(func)

    async def run(self):
        """运行服务器"""
        logger.info(f"NapCat WebSocket 服务器启动: ws://{self.host}:{self.port}")
        await self.app.run_task(host=self.host, port=self.port)

    async def start_background(self):
        """在后台启动服务器"""
        asyncio.create_task(self.run())
        logger.info("NapCat WebSocket 服务器已在后台启动")

