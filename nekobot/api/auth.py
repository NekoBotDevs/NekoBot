"""用户认证API"""
from quart import request, jsonify, current_app
from nekobot.api import api_bp
from nekobot.core.db.models import User
from nekobot.core.auth import require_auth


@api_bp.route("/auth/login", methods=["POST"])
async def login():
    """用户登录
    
    Request Body:
        {
            "username": "nekobot",
            "password": "password"
        }
        
    Response:
        {
            "code": 0,
            "message": "登录成功",
            "data": {
                "token": "jwt_token",
                "user": {
                    "username": "nekobot"
                }
            }
        }
    """
    try:
        data = await request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"code": 400, "message": "用户名和密码不能为空"}), 400

        db_manager = current_app.config["db_manager"]
        auth_manager = current_app.config["auth_manager"]

        user = await db_manager.get_by_field(User, "username", username)

        if not user:
            return jsonify({"code": 401, "message": "用户名或密码错误"}), 401

        if not auth_manager.verify_password(password, user.password_hash):
            return jsonify({"code": 401, "message": "用户名或密码错误"}), 401

        token = auth_manager.create_token(user.id, user.username)

        return jsonify(
            {
                "code": 0,
                "message": "登录成功",
                "data": {
                    "token": token,
                    "user": {"username": user.username},
                },
            }
        )

    except Exception as e:
        return jsonify({"code": 500, "message": f"登录失败: {str(e)}"}), 500


@api_bp.route("/auth/change-password", methods=["POST"])
@require_auth(lambda: current_app.config["auth_manager"])
async def change_password():
    """修改密码
    
    Headers:
        Authorization: Bearer <token>
        
    Request Body:
        {
            "old_password": "old_password",
            "new_password": "new_password"
        }
        
    Response:
        {
            "code": 0,
            "message": "密码修改成功"
        }
    """
    try:
        data = await request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not old_password or not new_password:
            return (
                jsonify({"code": 400, "message": "旧密码和新密码不能为空"}),
                400,
            )

        if len(new_password) < 6:
            return jsonify({"code": 400, "message": "新密码长度不能少于6位"}), 400

        db_manager = current_app.config["db_manager"]
        auth_manager = current_app.config["auth_manager"]

        user = await db_manager.get_by_id(User, request.user_id)

        if not user:
            return jsonify({"code": 404, "message": "用户不存在"}), 404

        if not auth_manager.verify_password(old_password, user.password_hash):
            return jsonify({"code": 401, "message": "旧密码错误"}), 401

        user.password_hash = auth_manager.hash_password(new_password)
        await db_manager.update(user)

        return jsonify({"code": 0, "message": "密码修改成功"})

    except Exception as e:
        return (
            jsonify({"code": 500, "message": f"密码修改失败: {str(e)}"}),
            500,
        )


@api_bp.route("/auth/init", methods=["POST"])
async def init_user():
    """初始化用户
    
    用于首次使用时创建默认用户
    
    Request Body:
        {
            "username": "nekobot",
            "password": "new_password"
        }
        
    Response:
        {
            "code": 0,
            "message": "初始化成功"
        }
    """
    try:
        db_manager = current_app.config["db_manager"]
        auth_manager = current_app.config["auth_manager"]

        existing_users = await db_manager.get_all(User, limit=1)
        if existing_users:
            return jsonify({"code": 400, "message": "用户已存在,无需初始化"}), 400

        data = await request.get_json()
        username = data.get("username", "nekobot")
        password = data.get("password", "nekobot")

        if len(password) < 6:
            return jsonify({"code": 400, "message": "密码长度不能少于6位"}), 400

        user = User(
            username=username,
            password_hash=auth_manager.hash_password(password),
        )

        await db_manager.create(user)

        return jsonify({"code": 0, "message": "初始化成功"})

    except Exception as e:
        return jsonify({"code": 500, "message": f"初始化失败: {str(e)}"}), 500