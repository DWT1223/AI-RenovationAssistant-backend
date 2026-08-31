"""
JWT Token工具
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import get_settings

settings = get_settings()


class JWTTools:
    """JWT工具类"""

    @staticmethod
    def create_token(data: Dict[str, Any], expire_minutes: Optional[int] = None) -> str:
        """
        创建JWT Token

        Args:
            data: 要编码的数据
            expire_minutes: 过期时间（分钟），默认使用配置中的时间

        Returns:
            JWT Token字符串
        """
        if expire_minutes is None:
            expire_minutes = settings.jwt_expire_minutes

        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        to_encode = data.copy()
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        return jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT Token

        Args:
            token: JWT Token字符串

        Returns:
            解码后的数据，验证失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token已过期
            return None
        except jwt.InvalidTokenError:
            # Token无效
            return None

    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """
        从Token中获取用户ID

        Args:
            token: JWT Token字符串

        Returns:
            用户ID，验证失败返回None
        """
        payload = JWTTools.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None
