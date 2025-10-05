"""插件管理API"""
import os
import zipfile
import shutil
import subprocess
from pathlib import Path
from quart import request, jsonify, current_app
from nekobot.api import api_bp
from nekobot.core.db.models import Plugin
from nekobot.core.auth import require_auth
import yaml


@api_bp.route("/plugins", methods=["GET"])
@require_auth(lambda: current_app.config["auth_manager"])
async def get_plugins():
    """获取插件列表
    
    Response:
        {
            "code": 0,
            "data": {
                "plugins": [...]
            }
        }
    """
    try:
        db_manager = current_app.config["db_manager"]
        plugins = await db_manager.get_all(Plugin)

        plugins_data = [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "author": p.author,
                "enabled": p.enabled,
                "is_official": p.is_official,
                "repository": p.repository,
            }
            for p in plugins
        ]

        return jsonify({"code": 0, "data": {"plugins": plugins_data}})

    except Exception as e:
        return jsonify({"code": 500, "message": f"获取插件列表失败: {str(e)}"}), 500


@api_bp.route("/plugins/upload", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def upload_plugin():
    """上传插件
    
    Request:
        Content-Type: multipart/form-data
        file: 插件zip文件
        
    Response:
        {
            "code": 0,
            "message": "插件上传成功",
            "data": {
                "plugin_name": "plugin_name"
            }
        }
    """
    try:
        files = await request.files
        if "file" not in files:
            return jsonify({"code": 400, "message": "未上传文件"}), 400

        file = files["file"]
        if not file.filename.endswith(".zip"):
            return jsonify({"code": 400, "message": "仅支持zip格式"}), 400

        plugins_dir = Path("./data/plugins")
        temp_dir = Path("./data/temp")
        plugins_dir.mkdir(parents=True, exist_ok=True)
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_zip = temp_dir / file.filename
        await file.save(str(temp_zip))

        with zipfile.ZipFile(temp_zip, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        plugin_folders = [
            d for d in temp_dir.iterdir() if d.is_dir() and d.name != "__MACOSX"
        ]
        if not plugin_folders:
            temp_zip.unlink()
            return jsonify({"code": 400, "message": "无效的插件格式"}), 400

        plugin_folder = plugin_folders[0]
        metadata_path = plugin_folder / "metadata.yaml"

        if not metadata_path.exists():
            shutil.rmtree(temp_dir)
            return jsonify({"code": 400, "message": "缺少metadata.yaml文件"}), 400

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        plugin_name = metadata.get("name")
        if not plugin_name:
            shutil.rmtree(temp_dir)
            return jsonify({"code": 400, "message": "metadata.yaml缺少name字段"}), 400

        db_manager = current_app.config["db_manager"]
        existing = await db_manager.get_by_field(Plugin, "name", plugin_name)

        target_dir = plugins_dir / plugin_name
        if target_dir.exists():
            shutil.rmtree(target_dir)

        shutil.move(str(plugin_folder), str(target_dir))

        requirements_file = target_dir / "requirements.txt"
        if requirements_file.exists():
            result = subprocess.run(
                ["pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return jsonify(
                    {"code": 500, "message": f"安装依赖失败: {result.stderr}"}
                ), 500

        if existing:
            existing.version = metadata.get("version", "1.0.0")
            existing.description = metadata.get("description")
            existing.author = metadata.get("author")
            existing.repository = metadata.get("repository")
            await db_manager.update(existing)
        else:
            plugin = Plugin(
                name=plugin_name,
                version=metadata.get("version", "1.0.0"),
                description=metadata.get("description"),
                author=metadata.get("author"),
                repository=metadata.get("repository"),
                enabled=True,
                is_official=False,
                path=str(target_dir),
            )
            await db_manager.create(plugin)

        shutil.rmtree(temp_dir)

        return jsonify(
            {
                "code": 0,
                "message": "插件上传成功",
                "data": {"plugin_name": plugin_name},
            }
        )

    except Exception as e:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return jsonify({"code": 500, "message": f"插件上传失败: {str(e)}"}), 500


@api_bp.route("/plugins/<plugin_name>/toggle", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def toggle_plugin(plugin_name: str):
    """启用/禁用插件
    
    Request Body:
        {
            "enabled": true
        }
        
    Response:
        {
            "code": 0,
            "message": "插件状态更新成功"
        }
    """
    try:
        data = await request.get_json()
        enabled = data.get("enabled")

        if enabled is None:
            return jsonify({"code": 400, "message": "缺少enabled参数"}), 400

        db_manager = current_app.config["db_manager"]
        plugin = await db_manager.get_by_field(Plugin, "name", plugin_name)

        if not plugin:
            return jsonify({"code": 404, "message": "插件不存在"}), 404

        if plugin.is_official:
            return jsonify({"code": 403, "message": "官方插件不可禁用"}), 403

        plugin.enabled = enabled
        await db_manager.update(plugin)

        return jsonify({"code": 0, "message": "插件状态更新成功"})

    except Exception as e:
        return jsonify({"code": 500, "message": f"更新插件状态失败: {str(e)}"}), 500


@api_bp.route("/plugins/<plugin_name>", methods=["DELETE"])
@require_auth(lambda: current_app.config["auth_manager"])
async def delete_plugin(plugin_name: str):
    """卸载插件
    
    Response:
        {
            "code": 0,
            "message": "插件卸载成功"
        }
    """
    try:
        db_manager = current_app.config["db_manager"]
        plugin = await db_manager.get_by_field(Plugin, "name", plugin_name)

        if not plugin:
            return jsonify({"code": 404, "message": "插件不存在"}), 404

        if plugin.is_official:
            return jsonify({"code": 403, "message": "官方插件不可卸载"}), 403

        plugin_path = Path(plugin.path)
        if plugin_path.exists():
            shutil.rmtree(plugin_path)

        await db_manager.delete(plugin)

        return jsonify({"code": 0, "message": "插件卸载成功"})

    except Exception as e:
        return jsonify({"code": 500, "message": f"插件卸载失败: {str(e)}"}), 500


@api_bp.route("/plugins/<plugin_name>/update", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def update_plugin(plugin_name: str):
    """更新插件
    
    Response:
        {
            "code": 0,
            "message": "插件更新成功",
            "data": {
                "old_version": "1.0.0",
                "new_version": "1.0.1"
            }
        }
    """
    try:
        db_manager = current_app.config["db_manager"]
        plugin = await db_manager.get_by_field(Plugin, "name", plugin_name)

        if not plugin:
            return jsonify({"code": 404, "message": "插件不存在"}), 404

        if not plugin.repository:
            return jsonify({"code": 400, "message": "插件未配置仓库地址"}), 400

        old_version = plugin.version

        plugin_path = Path(plugin.path)
        if plugin_path.exists():
            result = subprocess.run(
                ["git", "-C", str(plugin_path), "pull"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return jsonify({"code": 500, "message": f"更新失败: {result.stderr}"}), 500

        metadata_path = plugin_path / "metadata.yaml"
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = yaml.safe_load(f)
            new_version = metadata.get("version", old_version)
        else:
            new_version = old_version

        plugin.version = new_version
        await db_manager.update(plugin)

        requirements_file = plugin_path / "requirements.txt"
        if requirements_file.exists():
            subprocess.run(
                ["pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
            )

        return jsonify(
            {
                "code": 0,
                "message": "插件更新成功",
                "data": {"old_version": old_version, "new_version": new_version},
            }
        )

    except Exception as e:
        return jsonify({"code": 500, "message": f"插件更新失败: {str(e)}"}), 500