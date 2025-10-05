"""MCP配置API"""
from quart import request, jsonify, current_app
from nekobot.api import api_bp
from nekobot.core.auth import require_auth


@api_bp.route("/mcp/servers", methods=["GET"])
@require_auth(lambda: current_app.config["auth_manager"])
async def get_mcp_servers():
    """获取MCP服务器列表
    
    Response:
        {
            "code": 0,
            "data": {
                "servers": [...]
            }
        }
    """
    try:
        config_manager = current_app.config["config_manager"]
        mcp_config = config_manager.load_config("mcpserver.json", {})
        
        servers = mcp_config.get("servers", {})
        servers_list = [
            {
                "name": name,
                "enabled": server.get("enabled", True),
                "config": server.get("config", {}),
            }
            for name, server in servers.items()
        ]

        return jsonify({"code": 0, "data": {"servers": servers_list}})

    except Exception as e:
        return (
            jsonify({"code": 500, "message": f"获取MCP服务器列表失败: {str(e)}"}),
            500,
        )


@api_bp.route("/mcp/servers/<server_name>", methods=["PUT"])
@require_auth(lambda: current_app.config["auth_manager"])
async def update_mcp_server(server_name: str):
    """更新MCP服务器配置
    
    Request Body:
        {
            "enabled": true,
            "config": {
                "key": "value"
            }
        }
        
    Response:
        {
            "code": 0,
            "message": "MCP服务器配置更新成功"
        }
    """
    try:
        data = await request.get_json()
        enabled = data.get("enabled")
        config = data.get("config", {})

        config_manager = current_app.config["config_manager"]
        mcp_config = config_manager.load_config("mcpserver.json", {})

        if "servers" not in mcp_config:
            mcp_config["servers"] = {}

        if server_name not in mcp_config["servers"]:
            mcp_config["servers"][server_name] = {}

        if enabled is not None:
            mcp_config["servers"][server_name]["enabled"] = enabled
        
        if config:
            mcp_config["servers"][server_name]["config"] = config

        config_manager.save_config("mcpserver.json", mcp_config)

        return jsonify({"code": 0, "message": "MCP服务器配置更新成功"})

    except Exception as e:
        return (
            jsonify({"code": 500, "message": f"更新MCP服务器配置失败: {str(e)}"}),
            500,
        )


@api_bp.route("/mcp/servers", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def add_mcp_server():
    """添加MCP服务器
    
    Request Body:
        {
            "name": "server_name",
            "enabled": true,
            "config": {
                "key": "value"
            }
        }
        
    Response:
        {
            "code": 0,
            "message": "MCP服务器添加成功"
        }
    """
    try:
        data = await request.get_json()
        name = data.get("name")
        enabled = data.get("enabled", True)
        config = data.get("config", {})

        if not name:
            return jsonify({"code": 400, "message": "服务器名称不能为空"}), 400

        config_manager = current_app.config["config_manager"]
        mcp_config = config_manager.load_config("mcpserver.json", {})

        if "servers" not in mcp_config:
            mcp_config["servers"] = {}

        if name in mcp_config["servers"]:
            return jsonify({"code": 400, "message": "服务器已存在"}), 400

        mcp_config["servers"][name] = {"enabled": enabled, "config": config}

        config_manager.save_config("mcpserver.json", mcp_config)

        return jsonify({"code": 0, "message": "MCP服务器添加成功"})

    except Exception as e:
        return (
            jsonify({"code": 500, "message": f"添加MCP服务器失败: {str(e)}"}),
            500,
        )


@api_bp.route("/mcp/servers/<server_name>", methods=["DELETE"])
@require_auth(lambda: current_app.config["auth_manager"])
async def delete_mcp_server(server_name: str):
    """删除MCP服务器
    
    Response:
        {
            "code": 0,
            "message": "MCP服务器删除成功"
        }
    """
    try:
        config_manager = current_app.config["config_manager"]
        mcp_config = config_manager.load_config("mcpserver.json", {})

        if "servers" not in mcp_config or server_name not in mcp_config["servers"]:
            return jsonify({"code": 404, "message": "服务器不存在"}), 404

        del mcp_config["servers"][server_name]
        config_manager.save_config("mcpserver.json", mcp_config)

        return jsonify({"code": 0, "message": "MCP服务器删除成功"})

    except Exception as e:
        return (
            jsonify({"code": 500, "message": f"删除MCP服务器失败: {str(e)}"}),
            500,
        )