"""
平台适配器管理 API
"""

from quart import Blueprint, request, jsonify
from nekobot.auth.jwt_auth import require_auth
from nekobot.core.adapter_manager import get_adapter_manager
from nekobot.utils.logger import get_logger

logger = get_logger("api.platform")

platform_bp = Blueprint("platform", __name__, url_prefix="/platforms")


@platform_bp.route("/list", methods=["GET"])
@require_auth
async def list_platforms():
    """获取平台适配器列表"""
    try:
        manager = get_adapter_manager()
        adapters = manager.get_all_adapters()

        result = []
        for name, adapter in adapters.items():
            result.append(
                {
                    "name": name,
                    "type": adapter["type"],
                    "is_active": adapter["is_active"],
                }
            )

        return jsonify({"adapters": result}), 200

    except Exception as e:
        logger.error(f"获取平台适配器列表失败: {e}")
        return jsonify({"error": "获取平台适配器列表失败"}), 500


@platform_bp.route("/add", methods=["POST"])
@require_auth
async def add_platform():
    """添加平台适配器"""
    try:
        data = await request.get_json()

        name = data.get("name")
        platform_type = data.get("platform_type")
        config = data.get("config", {})

        if not name or not platform_type:
            return jsonify({"error": "缺少必要参数"}), 400

        manager = get_adapter_manager()
        success = await manager.add_adapter(name, platform_type, config)

        if success:
            logger.info(f"平台适配器已添加: {name}")
            return jsonify({"message": "平台适配器已添加"}), 200
        else:
            return jsonify({"error": "添加平台适配器失败"}), 400

    except Exception as e:
        logger.error(f"添加平台适配器失败: {e}")
        return jsonify({"error": "添加平台适配器失败"}), 500


@platform_bp.route("/<platform_name>", methods=["DELETE"])
@require_auth
async def remove_platform(platform_name: str):
    """移除平台适配器"""
    try:
        manager = get_adapter_manager()
        success = await manager.remove_adapter(platform_name)

        if success:
            logger.info(f"平台适配器已移除: {platform_name}")
            return jsonify({"message": "平台适配器已移除"}), 200
        else:
            return jsonify({"error": "移除平台适配器失败"}), 400

    except Exception as e:
        logger.error(f"移除平台适配器失败: {e}")
        return jsonify({"error": "移除平台适配器失败"}), 500

