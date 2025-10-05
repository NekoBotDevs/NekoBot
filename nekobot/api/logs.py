"""日志管理API"""
import asyncio
from datetime import datetime
from quart import request, jsonify, current_app, websocket
from nekobot.api import api_bp
from nekobot.core.db.models import SystemLog
from nekobot.core.auth import require_auth


@api_bp.route("/logs", methods=["GET"])
@require_auth(lambda: current_app.config["auth_manager"])
async def get_logs():
    """获取日志
    
    Query Parameters:
        level: 日志级别(DEBUG/INFO/WARNING/ERROR/CRITICAL)
        limit: 返回条数(默认100)
        search: 搜索关键词
        
    Response:
        {
            "code": 0,
            "data": {
                "logs": [...]
            }
        }
    """
    try:
        level = request.args.get("level")
        limit = int(request.args.get("limit", 100))
        search = request.args.get("search")

        db_manager = current_app.config["db_manager"]
        
        logs = await db_manager.get_all(SystemLog, limit=limit)

        filtered_logs = logs
        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]
        
        if search:
            filtered_logs = [
                log
                for log in filtered_logs
                if search.lower() in log.message.lower()
            ]

        logs_data = [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "module": log.module,
            }
            for log in filtered_logs
        ]

        return jsonify({"code": 0, "data": {"logs": logs_data}})

    except Exception as e:
        return jsonify({"code": 500, "message": f"获取日志失败: {str(e)}"}), 500


@api_bp.websocket("/logs/stream")
async def logs_stream():
    """日志WebSocket实时推送
    
    连接参数:
        token: JWT令牌
        
    推送消息格式:
        {
            "timestamp": "2025-01-01T00:00:00Z",
            "level": "INFO",
            "message": "日志消息",
            "module": "nekobot.core"
        }
    """
    try:
        token = websocket.args.get("token")
        if not token:
            await websocket.close(1008, "缺少认证令牌")
            return

        auth_manager = current_app.config["auth_manager"]
        payload = auth_manager.verify_token(token)
        if not payload:
            await websocket.close(1008, "令牌无效或已过期")
            return

        log_queue = asyncio.Queue()
        
        if "log_queues" not in current_app.config:
            current_app.config["log_queues"] = []
        current_app.config["log_queues"].append(log_queue)

        try:
            while True:
                log_data = await log_queue.get()
                await websocket.send_json(log_data)
        except asyncio.CancelledError:
            pass
        finally:
            current_app.config["log_queues"].remove(log_queue)

    except Exception as e:
        await websocket.close(1011, f"错误: {str(e)}")


async def broadcast_log(app, level: str, message: str, module: str):
    """广播日志到所有WebSocket连接
    
    Args:
        app: Quart应用实例
        level: 日志级别
        message: 日志消息
        module: 模块名
    """
    if "log_queues" not in app.config:
        return

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "module": module,
    }

    for queue in app.config["log_queues"]:
        try:
            await queue.put(log_data)
        except Exception:
            pass


@api_bp.route("/logs/clear", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def clear_logs():
    """清除日志
    
    Request Body:
        {
            "before_date": "2025-01-01T00:00:00Z"  # 可选,清除此日期之前的日志
        }
        
    Response:
        {
            "code": 0,
            "message": "日志清除成功",
            "data": {
                "deleted_count": 100
            }
        }
    """
    try:
        data = await request.get_json() or {}
        before_date = data.get("before_date")

        db_manager = current_app.config["db_manager"]
        logs = await db_manager.get_all(SystemLog, limit=10000)

        deleted_count = 0
        for log in logs:
            if before_date:
                target_date = datetime.fromisoformat(before_date.replace("Z", "+00:00"))
                if log.timestamp < target_date:
                    await db_manager.delete(log)
                    deleted_count += 1
            else:
                await db_manager.delete(log)
                deleted_count += 1

        return jsonify(
            {
                "code": 0,
                "message": "日志清除成功",
                "data": {"deleted_count": deleted_count},
            }
        )

    except Exception as e:
        return jsonify({"code": 500, "message": f"清除日志失败: {str(e)}"}), 500