"""
配置管理 API
"""

from quart import Blueprint, request, jsonify
from nekobot.auth.jwt_auth import require_auth
from nekobot.config.manager import get_config_manager
from nekobot.utils.logger import get_logger

logger = get_logger("api.config")

config_bp = Blueprint("config", __name__, url_prefix="/config")


@config_bp.route("/", methods=["GET"])
@require_auth
async def get_config():
    """获取配置"""
    try:
        manager = get_config_manager()
        config = manager.get_all()

        # 移除敏感信息
        if "security" in config:
            config["security"] = dict.fromkeys(config["security"].keys(), "***")

        return jsonify({"config": config}), 200
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        return jsonify({"error": "获取配置失败"}), 500


@config_bp.route("/", methods=["PUT"])
@require_auth
async def update_config():
    """更新配置"""
    try:
        data = await request.get_json()
        key = data.get("key")
        value = data.get("value")

        if not key:
            return jsonify({"error": "缺少 key 参数"}), 400

        manager = get_config_manager()
        manager.set(key, value)

        logger.info(f"配置已更新: {key}")
        return jsonify({"message": "配置已更新"}), 200

    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        return jsonify({"error": "更新配置失败"}), 500


@config_bp.route("/reload", methods=["POST"])
@require_auth
async def reload_config():
    """重新加载配置"""
    try:
        manager = get_config_manager()
        manager.reload()

        logger.info("配置已重新加载")
        return jsonify({"message": "配置已重新加载"}), 200

    except Exception as e:
        logger.error(f"重新加载配置失败: {e}")
        return jsonify({"error": "重新加载配置失败"}), 500

