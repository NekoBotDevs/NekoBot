"""
JWT 认证系统
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import bcrypt
from functools import wraps
from quart import request, jsonify

from nekobot.config.manager import get_config_manager
from nekobot.utils.logger import get_logger

logger = get_logger("auth")


class JWTAuth:
    """JWT 认证管理器"""

    def __init__(self):
        self.config_manager = get_config_manager()

    def _get_secret_key(self) -> str:
        """获取 JWT 密钥"""
        secret = self.config_manager.get("security.jwt_secret")
        if not secret:
            secret = secrets.token_urlsafe(32)
            self.config_manager.set("security.jwt_secret", secret)
        return secret

    def _get_algorithm(self) -> str:
        """获取 JWT 算法"""
        return self.config_manager.get("security.jwt_algorithm", "HS256")

    def _get_expire_hours(self) -> int:
        """获取 JWT 过期时间（小时）"""
        return self.config_manager.get("security.jwt_expire_hours", 24)

    def hash_password(self, password: str) -> str:
        """对密码进行哈希"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False

    def create_token(self, user_id: int, username: str) -> str:
        """创建 JWT Token"""
        expire_hours = self._get_expire_hours()
        expire_time = datetime.utcnow() + timedelta(hours=expire_hours)

        payload = {
            "user_id": user_id,
            "username": username,
            "exp": expire_time,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self._get_secret_key(), algorithm=self._get_algorithm())
        logger.info(f"为用户 {username} 创建了新 Token")
        return token

    def decode_token(self, token: str) -> Optional[Dict]:
        """解码 JWT Token"""
        try:
            payload = jwt.decode(
                token, self._get_secret_key(), algorithms=[self._get_algorithm()]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token 已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的 Token: {e}")
            return None

    def invalidate_all_tokens(self):
        """使所有现有 Token 失效（通过更换密钥）"""
        new_secret = secrets.token_urlsafe(32)
        self.config_manager.set("security.jwt_secret", new_secret)
        logger.warning("JWT 密钥已更换，所有旧 Token 已失效")


# 全局认证实例
jwt_auth = JWTAuth()


def require_auth(f):
    """装饰器：要求 JWT 认证"""

    @wraps(f)
    async def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "缺少认证令牌"}), 401

        try:
            token_type, token = auth_header.split(" ")
            if token_type.lower() != "bearer":
                return jsonify({"error": "无效的认证类型"}), 401
        except ValueError:
            return jsonify({"error": "无效的认证头格式"}), 401

        payload = jwt_auth.decode_token(token)
        if not payload:
            return jsonify({"error": "认证令牌无效或已过期"}), 401

        # 将用户信息添加到请求上下文
        request.user_id = payload.get("user_id")
        request.username = payload.get("username")

        return await f(*args, **kwargs)

    return decorated_function

