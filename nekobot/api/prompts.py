"""提示词管理API"""
from pathlib import Path
from quart import request, jsonify, current_app
from nekobot.api import api_bp
from nekobot.core.db.models import Prompt
from nekobot.core.auth import require_auth


@api_bp.route("/prompts", methods=["GET"])
@require_auth(lambda: current_app.config["auth_manager"])
async def get_prompts():
    """获取提示词列表
    
    Response:
        {
            "code": 0,
            "data": {
                "prompts": [...]
            }
        }
    """
    try:
        db_manager = current_app.config["db_manager"]
        prompts = await db_manager.get_all(Prompt)

        prompts_data = [
            {
                "id": p.id,
                "name": p.name,
                "content": p.content,
                "category": p.category,
                "is_active": p.is_active,
                "created_at": p.created_at.isoformat(),
            }
            for p in prompts
        ]

        return jsonify({"code": 0, "data": {"prompts": prompts_data}})

    except Exception as e:
        return jsonify({"code": 500, "message": f"获取提示词列表失败: {str(e)}"}), 500


@api_bp.route("/prompts", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def create_prompt():
    """创建提示词
    
    Request Body:
        {
            "name": "提示词名称",
            "content": "提示词内容",
            "category": "分类",
            "is_active": true
        }
        
    Response:
        {
            "code": 0,
            "message": "提示词创建成功",
            "data": {
                "id": 1
            }
        }
    """
    try:
        data = await request.get_json()
        name = data.get("name")
        content = data.get("content")
        category = data.get("category")
        is_active = data.get("is_active", True)

        if not name or not content:
            return jsonify({"code": 400, "message": "名称和内容不能为空"}), 400

        db_manager = current_app.config["db_manager"]

        prompt = Prompt(
            name=name,
            content=content,
            category=category,
            is_active=is_active,
        )

        created = await db_manager.create(prompt)

        return jsonify(
            {
                "code": 0,
                "message": "提示词创建成功",
                "data": {"id": created.id},
            }
        )

    except Exception as e:
        return jsonify({"code": 500, "message": f"创建提示词失败: {str(e)}"}), 500


@api_bp.route("/prompts/upload", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def upload_prompt():
    """上传提示词文件
    
    Request:
        Content-Type: multipart/form-data
        file: Markdown或txt文件
        name: 提示词名称(可选)
        category: 分类(可选)
        
    Response:
        {
            "code": 0,
            "message": "提示词上传成功",
            "data": {
                "id": 1
            }
        }
    """
    try:
        files = await request.files
        if "file" not in files:
            return jsonify({"code": 400, "message": "未上传文件"}), 400

        file = files["file"]
        filename = file.filename

        if not (filename.endswith(".md") or filename.endswith(".txt")):
            return jsonify({"code": 400, "message": "仅支持.md和.txt格式"}), 400

        form = await request.form
        name = form.get("name", Path(filename).stem)
        category = form.get("category")

        content_bytes = await file.read()
        content = content_bytes.decode("utf-8")

        db_manager = current_app.config["db_manager"]

        prompt = Prompt(
            name=name, content=content, category=category, is_active=True
        )

        created = await db_manager.create(prompt)

        return jsonify(
            {
                "code": 0,
                "message": "提示词上传成功",
                "data": {"id": created.id},
            }
        )

    except Exception as e:
        return jsonify({"code": 500, "message": f"上传提示词失败: {str(e)}"}), 500


@api_bp.route("/prompts/<int:prompt_id>", methods=["PUT"])
@require_auth(lambda: current_app.config["auth_manager"])
async def update_prompt(prompt_id: int):
    """更新提示词
    
    Request Body:
        {
            "name": "提示词名称",
            "content": "提示词内容",
            "category": "分类",
            "is_active": true
        }
        
    Response:
        {
            "code": 0,
            "message": "提示词更新成功"
        }
    """
    try:
        data = await request.get_json()

        db_manager = current_app.config["db_manager"]
        prompt = await db_manager.get_by_id(Prompt, prompt_id)

        if not prompt:
            return jsonify({"code": 404, "message": "提示词不存在"}), 404

        if "name" in data:
            prompt.name = data["name"]
        if "content" in data:
            prompt.content = data["content"]
        if "category" in data:
            prompt.category = data["category"]
        if "is_active" in data:
            prompt.is_active = data["is_active"]

        await db_manager.update(prompt)

        return jsonify({"code": 0, "message": "提示词更新成功"})

    except Exception as e:
        return jsonify({"code": 500, "message": f"更新提示词失败: {str(e)}"}), 500


@api_bp.route("/prompts/<int:prompt_id>", methods=["DELETE"])
@require_auth(lambda: current_app.config["auth_manager"])
async def delete_prompt(prompt_id: int):
    """删除提示词
    
    Response:
        {
            "code": 0,
            "message": "提示词删除成功"
        }
    """
    try:
        db_manager = current_app.config["db_manager"]
        success = await db_manager.delete_by_id(Prompt, prompt_id)

        if not success:
            return jsonify({"code": 404, "message": "提示词不存在"}), 404

        return jsonify({"code": 0, "message": "提示词删除成功"})

    except Exception as e:
        return jsonify({"code": 500, "message": f"删除提示词失败: {str(e)}"}), 500