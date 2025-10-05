"""LLM配置API"""
import json
from quart import request, jsonify, current_app
from nekobot.api import api_bp
from nekobot.core.db.models import LLMProvider
from nekobot.core.auth import require_auth


@api_bp.route("/llm/providers", methods=["GET"])
@require_auth(lambda: current_app.config["auth_manager"])
async def get_llm_providers():
    """获取LLM提供商列表
    
    Response:
        {
            "code": 0,
            "data": {
                "providers": [...]
            }
        }
    """
    try:
        db_manager = current_app.config["db_manager"]
        providers = await db_manager.get_all(LLMProvider)

        providers_data = [
            {
                "id": p.id,
                "name": p.name,
                "type": p.provider_type,
                "api_keys": json.loads(p.api_keys) if p.api_keys else [],
                "model": p.model,
                "base_url": p.base_url,
                "timeout": p.timeout,
                "enabled": p.enabled,
                "config": json.loads(p.config) if p.config else {},
            }
            for p in providers
        ]

        return jsonify({"code": 0, "data": {"providers": providers_data}})

    except Exception as e:
        return (
            jsonify({"code": 500, "message": f"获取LLM提供商列表失败: {str(e)}"}),
            500,
        )


@api_bp.route("/llm/providers", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def add_llm_provider():
    """添加LLM提供商
    
    Request Body:
        {
            "name": "OpenAI",
            "type": "openai",
            "api_keys": ["sk-xxx"],
            "model": "gpt-4",
            "base_url": "https://api.openai.com/v1",
            "timeout": 60,
            "config": {}
        }
        
    Response:
        {
            "code": 0,
            "message": "LLM提供商添加成功",
            "data": {
                "id": 1
            }
        }
    """
    try:
        data = await request.get_json()
        name = data.get("name")
        provider_type = data.get("type")
        api_keys = data.get("api_keys", [])
        model = data.get("model")
        base_url = data.get("base_url")
        timeout = data.get("timeout", 60)
        config = data.get("config", {})

        if not name or not provider_type or not model:
            return (
                jsonify({"code": 400, "message": "缺少必填字段"}),
                400,
            )

        if not api_keys or not isinstance(api_keys, list):
            return (
                jsonify({"code": 400, "message": "api_keys必须是非空数组"}),
                400,
            )

        db_manager = current_app.config["db_manager"]

        provider = LLMProvider(
            name=name,
            provider_type=provider_type,
            api_keys=json.dumps(api_keys),
            model=model,
            base_url=base_url,
            timeout=timeout,
            enabled=True,
            config=json.dumps(config),
        )

        created = await db_manager.create(provider)

        return jsonify(
            {
                "code": 0,
                "message": "LLM提供商添加成功",
                "data": {"id": created.id},
            }
        )

    except Exception as e:
        return (
            jsonify({"code": 500, "message": f"添加LLM提供商失败: {str(e)}"}),
            500,
        )


@api_bp.route("/llm/providers/<int:provider_id>", methods=["PUT"])
@require_auth(lambda: current_app.config["auth_manager"])
async def update_llm_provider(provider_id: int):
    """更新LLM提供商
    
    Request Body:
        {
            "name": "OpenAI",
            "type": "openai",
            "api_keys": ["sk-xxx"],
            "model": "gpt-4",
            "base_url": "https://api.openai.com/v1",
            "timeout": 60,
            "enabled": true,
            "config": {}
        }
        
    Response:
        {
            "code": 0,
            "message": "LLM提供商更新成功"
        }
    """
    try:
        data = await request.get_json()

        db_manager = current_app.config["db_manager"]
        provider = await db_manager.get_by_id(LLMProvider, provider_id)

        if not provider:
            return jsonify({"code": 404, "message": "LLM提供商不存在"}), 404

        if "name" in data:
            provider.name = data["name"]
        if "type" in data:
            provider.provider_type = data["type"]
        if "api_keys" in data:
            api_keys = data["api_keys"]
            if not isinstance(api_keys, list):
                return (
                    jsonify({"code": 400, "message": "api_keys必须是数组"}),
                    400,
                )
            provider.api_keys = json.dumps(api_keys)
        if "model" in data:
            provider.model = data["model"]
        if "base_url" in data:
            provider.base_url = data["base_url"]
        if "timeout" in data:
            provider.timeout = data["timeout"]
        if "enabled" in data:
            provider.enabled = data["enabled"]
        if "config" in data:
            provider.config = json.dumps(data["config"])

        await db_manager.update(provider)

        return jsonify({"code": 0, "message": "LLM提供商更新成功"})

    except Exception as e:
        return (
            jsonify({"code": 500, "message": f"更新LLM提供商失败: {str(e)}"}),
            500,
        )


@api_bp.route("/llm/providers/<int:provider_id>", methods=["DELETE"])
@require_auth(lambda: current_app.config["auth_manager"])
async def delete_llm_provider(provider_id: int):
    """删除LLM提供商
    
    Response:
        {
            "code": 0,
            "message": "LLM提供商删除成功"
        }
    """
    try:
        db_manager = current_app.config["db_manager"]
        success = await db_manager.delete_by_id(LLMProvider, provider_id)

        if not success:
            return jsonify({"code": 404, "message": "LLM提供商不存在"}), 404

        return jsonify({"code": 0, "message": "LLM提供商删除成功"})

    except Exception as e:
        return (
            jsonify({"code": 500, "message": f"删除LLM提供商失败: {str(e)}"}),
            500,
        )