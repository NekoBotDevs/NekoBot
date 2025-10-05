"""平台适配器管理API"""
from quart import request, jsonify, current_app
from nekobot.api import api_bp
from nekobot.core.auth import require_auth


@api_bp.route("/adapters", methods=["GET"])
@require_auth(lambda: current_app.config["auth_manager"])
async def get_adapters():
    """获取所有适配器状态
    
    Response:
        {
            "code": 0,
            "data": {
                "adapters": [
                    {
                        "name": "wecom",
                        "running": true,
                        "config": {...}
                    }
                ]
            }
        }
    """
    try:
        adapter_manager = current_app.config.get("adapter_manager")
        if not adapter_manager:
            return jsonify({"code": 500, "message": "适配器管理器未初始化"}), 500
        
        adapters = adapter_manager.get_all_adapters()
        adapters_data = [
            {
                "name": name,
                "running": adapter.is_running(),
                "platform": adapter.platform_name,
                "config": {
                    k: v for k, v in adapter.config.items() 
                    if k not in ["secret", "token", "api_key", "password"]
                }
            }
            for name, adapter in adapters.items()
        ]
        
        return jsonify({"code": 0, "data": {"adapters": adapters_data}})
    
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取适配器列表失败: {str(e)}"}), 500


@api_bp.route("/adapters/<adapter_name>/start", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def start_adapter(adapter_name: str):
    """启动指定适配器
    
    Response:
        {
            "code": 0,
            "message": "适配器启动成功"
        }
    """
    try:
        adapter_manager = current_app.config.get("adapter_manager")
        if not adapter_manager:
            return jsonify({"code": 500, "message": "适配器管理器未初始化"}), 500
        
        adapter = adapter_manager.get_adapter(adapter_name)
        if not adapter:
            return jsonify({"code": 404, "message": "适配器不存在"}), 404
        
        if adapter.is_running():
            return jsonify({"code": 400, "message": "适配器已在运行"}), 400
        
        await adapter.start()
        return jsonify({"code": 0, "message": "适配器启动成功"})
    
    except Exception as e:
        return jsonify({"code": 500, "message": f"启动适配器失败: {str(e)}"}), 500


@api_bp.route("/adapters/<adapter_name>/stop", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def stop_adapter(adapter_name: str):
    """停止指定适配器
    
    Response:
        {
            "code": 0,
            "message": "适配器停止成功"
        }
    """
    try:
        adapter_manager = current_app.config.get("adapter_manager")
        if not adapter_manager:
            return jsonify({"code": 500, "message": "适配器管理器未初始化"}), 500
        
        adapter = adapter_manager.get_adapter(adapter_name)
        if not adapter:
            return jsonify({"code": 404, "message": "适配器不存在"}), 404
        
        if not adapter.is_running():
            return jsonify({"code": 400, "message": "适配器未运行"}), 400
        
        await adapter.stop()
        return jsonify({"code": 0, "message": "适配器停止成功"})
    
    except Exception as e:
        return jsonify({"code": 500, "message": f"停止适配器失败: {str(e)}"}), 500


@api_bp.route("/adapters/<adapter_name>/config", methods=["PUT"])
@require_auth(lambda: current_app.config["auth_manager"])
async def update_adapter_config(adapter_name: str):
    """更新适配器配置
    
    Request Body:
        {
            "config": {
                "key": "value"
            }
        }
    
    Response:
        {
            "code": 0,
            "message": "配置更新成功"
        }
    """
    try:
        data = await request.get_json()
        config = data.get("config", {})
        
        config_manager = current_app.config["config_manager"]
        adapters_config = config_manager.load_config("adapters.json", {})
        
        if adapter_name not in adapters_config:
            adapters_config[adapter_name] = {}
        
        adapters_config[adapter_name].update(config)
        config_manager.save_config("adapters.json", adapters_config)
        
        return jsonify({"code": 0, "message": "配置更新成功"})
    
    except Exception as e:
        return jsonify({"code": 500, "message": f"更新配置失败: {str(e)}"}), 500