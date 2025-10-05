"""JWT认证模块"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from functools import wraps
import jwt
import bcrypt
from quart import request, jsonify
from nekobot.core.config import NekoConfigManager


class AuthManager:
    """认证管理器"""

    def __init__(self, config_manager: NekoConfigManager):
        """初始化认证管理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.jwt_secret = self._get_or_create_jwt_secret()
        self.jwt_algorithm = "HS256"
        self.jwt_expiration = 86400

    def _get_or_create_jwt_secret(self) -> str:
        """获取或创建JWT密钥"""
        secret = self.config_manager.get_config(
            "auth_config.json", "jwt_secret"
        )
        if not secret:
            secret = secrets.token_urlsafe(32)
            self.config_manager.update_config(
                "auth_config.json", "jwt_secret", secret
            )
        return secret

    def hash_password(self, password: str) -> str:
        """哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码
        
        Args:
            password: 明文密码
            hashed: 哈希密码
            
        Returns:
            是否匹配
        """
        return bcrypt.checkpw(
            password.encode("utf-8"), hashed.encode("utf-8")
        )

    def create_token(self, user_id: int, username: str) -> str:
        """创建JWT令牌
        
        Args:
            user_id: 用户ID
            username: 用户名
            
        Returns:
            JWT令牌
        """
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": datetime.utcnow()
            + timedelta(seconds=self.jwt_expiration),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_token(self, token: str) -> Optional[dict]:
        """验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            令牌载荷或None
        """
        try:
            payload = jwt.decode(
                token, self.jwt_secret, algorithms=[self.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


def require_auth(auth_manager: AuthManager):
    """JWT认证装饰器
    
    Args:
        auth_manager: 认证管理器实例
    """

    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify({"code": 401, "message": "缺少认证令牌"}), 401

            try:
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    return (
                        jsonify({"code": 401, "message": "无效的认证类型"}),
                        401,
                    )
            except ValueError:
                return jsonify({"code": 401, "message": "无效的认证格式"}), 401

            payload = auth_manager.verify_token(token)
            if not payload:
                return (
                    jsonify({"code": 401, "message": "令牌无效或已过期"}),
                    401,
                )

            request.user_id = payload.get("user_id")
            request.username = payload.get("username")

            return await f(*args, **kwargs)

        return decorated_function

    return decorator