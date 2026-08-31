"""
认证服务
"""
import httpx
import hashlib
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import LoginResponse, UserResponse, UserCreate
from app.utils.jwt import JWTTools


class AuthService:
    """认证服务"""

    def __init__(self, db: Session):
        self.db = db

    def _hash_password(self, password: str) -> str:
        """密码哈希（简单实现，生产环境应使用更安全的方式）"""
        return hashlib.sha256(password.encode()).hexdigest()

    async def wechat_login(self, code: str) -> LoginResponse:
        """
        微信登录

        Args:
            code: 微信登录code

        Returns:
            登录响应（包含token和用户信息）
        """
        # 调用微信接口获取openid
        openid = await self._get_wechat_openid(code)

        if not openid:
            raise ValueError("微信登录失败")

        # 查询或创建用户
        user = self._get_or_create_user(openid)

        # 生成token
        token = JWTTools.create_token({"user_id": user.id})

        # 构建响应
        user_response = UserResponse.model_validate(user)
        return LoginResponse(token=token, user=user_response)

    async def _get_wechat_openid(self, code: str) -> str:
        """
        调用微信接口获取openid

        Args:
            code: 微信登录code

        Returns:
            openid
        """
        # TODO: 替换为实际的微信AppID和AppSecret
        appid = "your_wechat_appid"
        secret = "your_wechat_secret"

        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": appid,
            "secret": secret,
            "js_code": code,
            "grant_type": "authorization_code"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()

                if "openid" in data:
                    return data["openid"]
                return None
        except Exception:
            # 开发环境返回模拟openid
            return f"mock_openid_{code}"

    def _get_or_create_user(self, openid: str) -> User:
        """
        查询或创建用户

        Args:
            openid: 微信openid

        Returns:
            用户对象
        """
        user = self.db.query(User).filter(User.openid == openid).first()

        if not user:
            # 创建新用户
            user = User(
                openid=openid,
                nickname=f"用户{openid[-6:]}",
                avatar=""
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

    def account_login(self, username: str, password: str) -> dict:
        """
        账号密码登录

        Args:
            username: 用户名或手机号
            password: 密码

        Returns:
            登录响应（包含token和用户信息）
        """
        password_hash = self._hash_password(password)

        # 查询用户（支持用户名或手机号登录）
        user = self.db.query(User).filter(
            (User.username == username) | (User.phone == username)
        ).first()

        if not user:
            raise ValueError("用户不存在")

        if user.password != password_hash:
            raise ValueError("密码错误")

        # 生成token
        token = JWTTools.create_token({"user_id": user.id})

        # 构建响应（返回字典而非Pydantic模型）
        return {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar or "",
                "phone": user.phone,
                "openid": user.openid
            }
        }

    def register(self, username: str, password: str, phone: str = None) -> dict:
        """
        注册账号

        Args:
            username: 用户名
            password: 密码
            phone: 手机号（可选）

        Returns:
            注册结果
        """
        password_hash = self._hash_password(password)

        # 检查用户名是否已存在
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError("用户名已存在")

        # 检查手机号是否已存在
        if phone:
            existing_phone = self.db.query(User).filter(User.phone == phone).first()
            if existing_phone:
                raise ValueError("手机号已被注册")

        # 创建用户
        user = User(
            username=username,
            password=password_hash,
            phone=phone,
            nickname=username,
            avatar=""
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return {
            "id": user.id,
            "username": user.username,
            "phone": user.phone,
            "nickname": user.nickname
        }

    def update_user_info(self, user_id: int, nickname: str = None, avatar: str = None, phone: str = None) -> User:
        """
        更新用户信息

        Args:
            user_id: 用户ID
            nickname: 昵称
            avatar: 头像
            phone: 手机号

        Returns:
            更新后的用户对象
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        if nickname is not None:
            user.nickname = nickname
        if avatar is not None:
            user.avatar = avatar
        if phone is not None:
            user.phone = phone

        self.db.commit()
        self.db.refresh(user)
        return user

    def send_sms_code(self, phone: str, scene: str = "login") -> dict:
        """
        发送短信验证码

        Args:
            phone: 手机号
            scene: 场景 (register/reset/login)

        Returns:
            发送结果
        """
        import random
        import time

        # 生成6位验证码
        code = str(random.randint(100000, 999999))

        # TODO: 实际调用短信服务商API发送验证码
        # 这里简化为模拟发送
        # 验证码存储到缓存（实际应使用Redis等缓存服务）
        # 这里为了演示直接返回成功

        return {
            "code": code,  # 开发环境返回验证码，方便测试
            "message": "验证码已发送"
        }

    def reset_password(self, phone: str, sms_code: str, new_password: str) -> dict:
        """
        重置密码

        Args:
            phone: 手机号
            sms_code: 短信验证码
            new_password: 新密码

        Returns:
            重置结果
        """
        # TODO: 验证短信验证码（实际应从缓存获取并验证）

        password_hash = self._hash_password(new_password)

        # 查询用户
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user:
            raise ValueError("该手机号未注册")

        # 更新密码
        user.password = password_hash
        self.db.commit()

        return {
            "message": "密码重置成功"
        }
