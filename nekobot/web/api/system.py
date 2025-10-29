"""
系统信息 API
"""

import psutil
from quart import Blueprint, jsonify
from nekobot.auth.jwt_auth import require_auth
from nekobot import __version__
from nekobot.utils.logger import get_logger

logger = get_logger("api.system")

system_bp = Blueprint("system", __name__, url_prefix="/system")


@system_bp.route("/info", methods=["GET"])
@require_auth
async def get_system_info():
    """获取系统信息"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return jsonify(
            {
                "version": __version__,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
            }
        ), 200

    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        return jsonify({"error": "获取系统信息失败"}), 500


@system_bp.route("/version", methods=["GET"])
async def get_version():
    """获取版本信息（无需认证）"""
    return jsonify({"version": __version__}), 200

