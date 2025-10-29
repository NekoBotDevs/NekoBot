"""
LLM 管理 API
"""

from quart import Blueprint, request, jsonify
from nekobot.auth.jwt_auth import require_auth
from nekobot.llm.manager import get_llm_manager
from nekobot.utils.logger import get_logger

logger = get_logger("api.llm")

llm_bp = Blueprint("llm", __name__, url_prefix="/llm")


@llm_bp.route("/providers", methods=["GET"])
@require_auth
async def list_providers():
    """获取 LLM 服务商列表"""
    try:
        manager = get_llm_manager()
        providers = manager.get_provider_list()
        return jsonify({"providers": providers}), 200
    except Exception as e:
        logger.error(f"获取服务商列表失败: {e}")
        return jsonify({"error": "获取服务商列表失败"}), 500


@llm_bp.route("/providers", methods=["POST"])
@require_auth
async def add_provider():
    """添加 LLM 服务商"""
    try:
        data = await request.get_json()

        name = data.get("name")
        provider_type = data.get("provider_type")
        api_keys = data.get("api_keys", [])
        model = data.get("model")
        base_url = data.get("base_url")
        config = data.get("config", {})

        if not name or not provider_type or not api_keys or not model:
            return jsonify({"error": "缺少必要参数"}), 400

        manager = get_llm_manager()
        success = await manager.add_provider(
            name=name,
            provider_type=provider_type,
            api_keys=api_keys,
            model=model,
            base_url=base_url,
            **config,
        )

        if success:
            logger.info(f"LLM 服务商已添加: {name}")
            return jsonify({"message": "服务商添加成功"}), 200
        else:
            return jsonify({"error": "添加服务商失败"}), 400

    except Exception as e:
        logger.error(f"添加服务商失败: {e}")
        return jsonify({"error": "添加服务商失败"}), 500


@llm_bp.route("/providers/<provider_name>", methods=["DELETE"])
@require_auth
async def remove_provider(provider_name: str):
    """移除 LLM 服务商"""
    try:
        manager = get_llm_manager()
        success = await manager.remove_provider(provider_name)

        if success:
            logger.info(f"LLM 服务商已移除: {provider_name}")
            return jsonify({"message": "服务商已移除"}), 200
        else:
            return jsonify({"error": "移除服务商失败"}), 400

    except Exception as e:
        logger.error(f"移除服务商失败: {e}")
        return jsonify({"error": "移除服务商失败"}), 500


@llm_bp.route("/providers/<provider_name>/test", methods=["POST"])
@require_auth
async def test_provider(provider_name: str):
    """测试 LLM 服务商连接"""
    try:
        manager = get_llm_manager()
        success = await manager.test_provider(provider_name)

        if success:
            return jsonify({"message": "连接测试成功"}), 200
        else:
            return jsonify({"error": "连接测试失败"}), 400

    except Exception as e:
        logger.error(f"测试连接失败: {e}")
        return jsonify({"error": "测试连接失败"}), 500


@llm_bp.route("/chat", methods=["POST"])
@require_auth
async def chat():
    """与 LLM 对话"""
    try:
        data = await request.get_json()

        provider_name = data.get("provider")
        messages = data.get("messages", [])

        if not provider_name or not messages:
            return jsonify({"error": "缺少必要参数"}), 400

        manager = get_llm_manager()
        response = await manager.chat(provider_name, messages)

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"对话失败: {e}")
        return jsonify({"error": f"对话失败: {str(e)}"}), 500

