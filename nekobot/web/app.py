"""
Quart Web 应用
"""

from pathlib import Path
from quart import Quart, send_from_directory
from quart_cors import cors

from nekobot.config.manager import get_config_manager
from nekobot.utils.logger import get_logger
from nekobot.web.api import register_api_routes
from nekobot.web.websocket import register_websocket_routes

logger = get_logger("web")


def create_app() -> Quart:
    """创建 Quart 应用"""
    app = Quart(__name__)

    # 获取配置
    config_manager = get_config_manager()
    cors_origins = config_manager.get("server.cors_origins", ["*"])

    # 启用 CORS
    app = cors(
        app,
        allow_origin=cors_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # 注册 API 路由
    register_api_routes(app)

    # 注册 WebSocket 路由
    register_websocket_routes(app)

    # 静态文件服务（前端仪表盘）
    dist_dir = Path("./data/dist")

    @app.route("/")
    async def index():
        """提供前端首页"""
        if (dist_dir / "index.html").exists():
            return await send_from_directory(str(dist_dir), "index.html")
        else:
            return {"message": "NekoBot API Server", "version": "1.0.0"}, 200

    @app.route("/<path:path>")
    async def serve_static(path):
        """提供静态文件"""
        if dist_dir.exists() and (dist_dir / path).exists():
            return await send_from_directory(str(dist_dir), path)
        elif (dist_dir / "index.html").exists():
            return await send_from_directory(str(dist_dir), "index.html")
        else:
            return {"error": "文件不存在"}, 404

    logger.info("Web 应用创建完成")
    return app

