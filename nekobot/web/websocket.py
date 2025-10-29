"""
WebSocket 路由
"""

from quart import websocket
from nekobot.utils.logger import log_handler, get_logger

logger = get_logger("websocket")


def register_websocket_routes(app):
    """注册 WebSocket 路由"""

    @app.websocket("/ws")
    async def ws_logs():
        """WebSocket 实时日志推送"""
        logger.info("WebSocket 客户端已连接")
        log_handler.add_client(websocket._get_current_object())

        try:
            # 发送历史日志
            history = log_handler.get_history(100)
            for log_entry in history:
                await websocket.send_json(log_entry)

            # 保持连接
            while True:
                message = await websocket.receive()
                # 可以处理客户端发送的消息
                if message == "ping":
                    await websocket.send_json({"type": "pong"})

        except Exception as e:
            logger.warning(f"WebSocket 连接关闭: {e}")
        finally:
            log_handler.remove_client(websocket._get_current_object())
            logger.info("WebSocket 客户端已断开")

