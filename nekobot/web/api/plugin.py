"""
插件管理 API
"""

from quart import Blueprint, request, jsonify
from nekobot.auth.jwt_auth import require_auth
from nekobot.plugin.manager import get_plugin_manager
from nekobot.utils.logger import get_logger

logger = get_logger("api.plugin")

plugin_bp = Blueprint("plugin", __name__, url_prefix="/plugins")


@plugin_bp.route("/list", methods=["GET"])
@require_auth
async def list_plugins():
    """获取插件列表"""
    try:
        manager = get_plugin_manager()
        plugins = manager.get_plugin_list()
        return jsonify({"plugins": plugins}), 200
    except Exception as e:
        logger.error(f"获取插件列表失败: {e}")
        return jsonify({"error": "获取插件列表失败"}), 500


@plugin_bp.route("/<plugin_name>/enable", methods=["POST"])
@require_auth
async def enable_plugin(plugin_name: str):
    """启用插件"""
    try:
        manager = get_plugin_manager()
        success = await manager.enable_plugin(plugin_name)

        if success:
            logger.info(f"插件已启用: {plugin_name}")
            return jsonify({"message": "插件已启用"}), 200
        else:
            return jsonify({"error": "启用插件失败"}), 400
    except Exception as e:
        logger.error(f"启用插件失败: {e}")
        return jsonify({"error": "启用插件失败"}), 500


@plugin_bp.route("/<plugin_name>/disable", methods=["POST"])
@require_auth
async def disable_plugin(plugin_name: str):
    """禁用插件"""
    try:
        manager = get_plugin_manager()
        success = await manager.disable_plugin(plugin_name)

        if success:
            logger.info(f"插件已禁用: {plugin_name}")
            return jsonify({"message": "插件已禁用"}), 200
        else:
            return jsonify({"error": "禁用插件失败"}), 400
    except Exception as e:
        logger.error(f"禁用插件失败: {e}")
        return jsonify({"error": "禁用插件失败"}), 500


@plugin_bp.route("/<plugin_name>/reload", methods=["POST"])
@require_auth
async def reload_plugin(plugin_name: str):
    """重载插件"""
    try:
        manager = get_plugin_manager()
        success = await manager.reload_plugin(plugin_name)

        if success:
            logger.info(f"插件已重载: {plugin_name}")
            return jsonify({"message": "插件已重载"}), 200
        else:
            return jsonify({"error": "重载插件失败"}), 400
    except Exception as e:
        logger.error(f"重载插件失败: {e}")
        return jsonify({"error": "重载插件失败"}), 500


@plugin_bp.route("/<plugin_name>/uninstall", methods=["DELETE"])
@require_auth
async def uninstall_plugin(plugin_name: str):
    """卸载插件"""
    try:
        manager = get_plugin_manager()
        success = await manager.unload_plugin(plugin_name)

        if success:
            logger.info(f"插件已卸载: {plugin_name}")
            return jsonify({"message": "插件已卸载"}), 200
        else:
            return jsonify({"error": "卸载插件失败"}), 400
    except Exception as e:
        logger.error(f"卸载插件失败: {e}")
        return jsonify({"error": "卸载插件失败"}), 500


@plugin_bp.route("/upload", methods=["POST"])
@require_auth
async def upload_plugin():
    """上传插件"""
    try:
        files = await request.files
        if "file" not in files:
            return jsonify({"error": "未上传文件"}), 400

        file = files["file"]
        if not file.filename.endswith(".zip"):
            return jsonify({"error": "只支持 ZIP 格式"}), 400

        # 保存文件
        from pathlib import Path

        temp_dir = Path("./data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        zip_path = temp_dir / file.filename

        await file.save(str(zip_path))

        # 安装插件
        manager = get_plugin_manager()
        success = await manager.install_plugin_from_zip(zip_path)

        # 删除临时文件
        zip_path.unlink()

        if success:
            logger.info(f"插件上传安装成功: {file.filename}")
            return jsonify({"message": "插件安装成功"}), 200
        else:
            return jsonify({"error": "插件安装失败"}), 400

    except Exception as e:
        logger.error(f"上传插件失败: {e}")
        return jsonify({"error": "上传插件失败"}), 500

