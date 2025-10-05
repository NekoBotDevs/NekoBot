"""Quart应用主入口"""
import os
from datetime import datetime
from pathlib import Path
from quart import Quart, send_from_directory
from quart_cors import cors
from nekobot.core.config import NekoConfigManager
from nekobot.core.db import DatabaseManager
from nekobot.core.auth import AuthManager
from nekobot.api import api_bp


def create_app(config_dir: str = "./data") -> Quart:
    """创建Quart应用实例
    
    Args:
        config_dir: 配置文件目录
        
    Returns:
        Quart应用实例
    """
    app = Quart(__name__)
    
    app = cors(app, allow_origin="*")
    
    app.config["config_manager"] = NekoConfigManager(config_dir)
    app.config["db_manager"] = DatabaseManager(f"{config_dir}/nekobot.db")
    app.config["auth_manager"] = AuthManager(app.config["config_manager"])
    app.config["version"] = "1.0.0"
    app.config["start_time"] = datetime.utcnow()
    
    app.register_blueprint(api_bp)
    
    dist_path = Path("./data/dist")
    
    @app.route("/")
    async def index():
        """提供Web仪表盘"""
        if not dist_path.exists():
            return {"message": "仪表盘未安装,请先下载并解压dist.zip到./data/dist"}, 404
        return await send_from_directory(dist_path, "index.html")
    
    @app.route("/<path:path>")
    async def static_files(path: str):
        """提供静态文件"""
        if not dist_path.exists():
            return {"message": "仪表盘未安装"}, 404
        return await send_from_directory(dist_path, path)
    
    @app.before_serving
    async def startup():
        """应用启动时初始化"""
        await app.config["db_manager"].init_db()
        print(f"[NekoBot] 数据库初始化完成")
        print(f"[NekoBot] 应用启动成功,监听端口 6285")
        print(f"[NekoBot] 访问 http://localhost:6285 使用Web仪表盘")
    
    @app.after_serving
    async def shutdown():
        """应用关闭时清理"""
        await app.config["db_manager"].close()
        print(f"[NekoBot] 应用已关闭")
    
    return app


async def run_app(host: str = "0.0.0.0", port: int = 6285):
    """运行Quart应用
    
    Args:
        host: 监听地址
        port: 监听端口
    """
    app = create_app()
    await app.run_task(host=host, port=port)