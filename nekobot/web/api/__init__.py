"""
API 路由模块
"""

from quart import Blueprint
from nekobot.web.api import auth, plugin, llm, config, system, platform

api_bp = Blueprint("api", __name__, url_prefix="/api")


def register_api_routes(app):
    """注册所有 API 路由"""
    # 注册子路由
    api_bp.register_blueprint(auth.auth_bp)
    api_bp.register_blueprint(plugin.plugin_bp)
    api_bp.register_blueprint(llm.llm_bp)
    api_bp.register_blueprint(config.config_bp)
    api_bp.register_blueprint(system.system_bp)
    api_bp.register_blueprint(platform.platform_bp)

    # 注册到主应用
    app.register_blueprint(api_bp)

