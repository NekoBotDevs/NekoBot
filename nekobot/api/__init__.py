"""API模块"""
from quart import Blueprint

# 创建API蓝图
api_bp = Blueprint("api", __name__, url_prefix="/api")

# 导入所有路由
from . import auth, plugins, llm, prompts, logs, system, mcp

__all__ = ["api_bp"]