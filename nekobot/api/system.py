"""系统管理API"""
import psutil
import subprocess
from pathlib import Path
from quart import request, jsonify, current_app
from nekobot.api import api_bp
from nekobot.core.auth import require_auth


@api_bp.route("/system/status", methods=["GET"])
@require_auth(lambda: current_app.config["auth_manager"])
async def get_system_status():
    """获取系统状态
    
    Response:
        {
            "code": 0,
            "data": {
                "version": "1.0.0",
                "uptime": 3600,
                "cpu_usage": 25.5,
                "memory_usage": 512,
                "plugin_count": 5,
                "platform_count": 3
            }
        }
    """
    try:
        from nekobot.core.db.models import Plugin

        db_manager = current_app.config["db_manager"]
        plugins = await db_manager.get_all(Plugin)
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        uptime = current_app.config.get("start_time", 0)
        if uptime:
            from datetime import datetime
            uptime = int((datetime.utcnow() - uptime).total_seconds())

        status_data = {
            "version": current_app.config.get("version", "1.0.0"),
            "uptime": uptime,
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": memory_info.rss // (1024 * 1024),
            "plugin_count": len(plugins),
            "platform_count": 0,
        }

        return jsonify({"code": 0, "data": status_data})

    except Exception as e:
        return jsonify({"code": 500, "message": f"获取系统状态失败: {str(e)}"}), 500


@api_bp.route("/system/check-update", methods=["GET"])
@require_auth(lambda: current_app.config["auth_manager"])
async def check_update():
    """检查更新
    
    Response:
        {
            "code": 0,
            "data": {
                "current_version": "1.0.0",
                "latest_version": "1.0.1",
                "has_update": true,
                "changelog": "更新说明"
            }
        }
    """
    try:
        import aiohttp

        current_version = current_app.config.get("version", "1.0.0")
        
        repo_url = "https://api.github.com/repos/NekoBotDevs/NekoBot/releases/latest"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(repo_url) as resp:
                if resp.status != 200:
                    return jsonify({"code": 500, "message": "检查更新失败"}), 500
                
                data = await resp.json()
                latest_version = data.get("tag_name", "").lstrip("v")
                changelog = data.get("body", "")
                
                has_update = latest_version != current_version

                return jsonify(
                    {
                        "code": 0,
                        "data": {
                            "current_version": current_version,
                            "latest_version": latest_version,
                            "has_update": has_update,
                            "changelog": changelog,
                        },
                    }
                )

    except Exception as e:
        return jsonify({"code": 500, "message": f"检查更新失败: {str(e)}"}), 500


@api_bp.route("/system/update", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def update_system():
    """执行更新
    
    Request Body:
        {
            "version": "1.0.1",
            "branch": "main"
        }
        
    Response:
        {
            "code": 0,
            "message": "更新任务已启动"
        }
    """
    try:
        data = await request.get_json()
        version = data.get("version")
        branch = data.get("branch", "main")

        project_root = Path(__file__).parent.parent.parent

        if (project_root / ".git").exists():
            result = subprocess.run(
                ["git", "fetch", "origin", branch],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return jsonify({"code": 500, "message": f"更新失败: {result.stderr}"}), 500

            result = subprocess.run(
                ["git", "checkout", branch],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return jsonify({"code": 500, "message": f"更新失败: {result.stderr}"}), 500

            result = subprocess.run(
                ["git", "pull", "origin", branch],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return jsonify({"code": 500, "message": f"更新失败: {result.stderr}"}), 500

            return jsonify({"code": 0, "message": "更新任务已启动,请重启应用以应用更新"})
        else:
            return jsonify({"code": 400, "message": "当前不是git仓库,无法使用git更新"}), 400

    except Exception as e:
        return jsonify({"code": 500, "message": f"更新失败: {str(e)}"}), 500


@api_bp.route("/system/restart", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def restart_system():
    """重启系统
    
    Response:
        {
            "code": 0,
            "message": "系统将在3秒后重启"
        }
    """
    try:
        import asyncio
        import sys

        async def delayed_restart():
            await asyncio.sleep(3)
            import os
            os.execv(sys.executable, [sys.executable] + sys.argv)

        asyncio.create_task(delayed_restart())

        return jsonify({"code": 0, "message": "系统将在3秒后重启"})

    except Exception as e:
        return jsonify({"code": 500, "message": f"重启失败: {str(e)}"}), 500