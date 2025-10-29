"""
认证 API
"""

from quart import Blueprint, request, jsonify
from nekobot.auth.jwt_auth import jwt_auth, require_auth
from nekobot.database.engine import get_db_manager
from nekobot.database.models import User
from nekobot.utils.logger import get_logger
from sqlmodel import select

logger = get_logger("api.auth")

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
async def login():
    """用户登录"""
    try:
        data = await request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400

        db_manager = get_db_manager()

        async with db_manager.async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"用户不存在: {username}")
                return jsonify({"error": "用户名或密码错误"}), 401

            if not jwt_auth.verify_password(password, user.password_hash):
                logger.warning(f"密码错误: {username}")
                return jsonify({"error": "用户名或密码错误"}), 401

            if not user.is_active:
                return jsonify({"error": "用户已被禁用"}), 403

            token = jwt_auth.create_token(user.id, user.username)

            logger.info(f"用户登录成功: {username}")

            return jsonify(
                {
                    "token": token,
                    "username": user.username,
                    "must_change_password": user.must_change_password,
                }
            ), 200

    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({"error": "登录失败"}), 500


@auth_bp.route("/change-password", methods=["POST"])
@require_auth
async def change_password():
    """修改密码"""
    try:
        data = await request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not old_password or not new_password:
            return jsonify({"error": "旧密码和新密码不能为空"}), 400

        if len(new_password) < 6:
            return jsonify({"error": "新密码长度至少为 6 位"}), 400

        db_manager = get_db_manager()

        async with db_manager.async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == request.user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({"error": "用户不存在"}), 404

            if not jwt_auth.verify_password(old_password, user.password_hash):
                return jsonify({"error": "旧密码错误"}), 401

            user.password_hash = jwt_auth.hash_password(new_password)
            user.must_change_password = False
            session.add(user)
            await session.commit()

            # 使所有旧 Token 失效
            jwt_auth.invalidate_all_tokens()

            logger.info(f"用户 {user.username} 修改密码成功")

            return jsonify({"message": "密码修改成功，请重新登录"}), 200

    except Exception as e:
        logger.error(f"修改密码失败: {e}")
        return jsonify({"error": "修改密码失败"}), 500


@auth_bp.route("/profile", methods=["GET"])
@require_auth
async def get_profile():
    """获取用户信息"""
    try:
        db_manager = get_db_manager()

        async with db_manager.async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == request.user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({"error": "用户不存在"}), 404

            return jsonify(
                {
                    "username": user.username,
                    "is_active": user.is_active,
                    "must_change_password": user.must_change_password,
                    "created_at": user.created_at.isoformat(),
                }
            ), 200

    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return jsonify({"error": "获取用户信息失败"}), 500

