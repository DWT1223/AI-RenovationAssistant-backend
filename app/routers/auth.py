"""
认证路由
"""
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import LoginRequest
from app.services.auth_service import AuthService
from app.utils.response import Response

router = APIRouter(prefix="/api/auth", tags=["认证"])


class AccountLoginRequest(BaseModel):
    """账号登录请求"""
    username: str
    password: str


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    微信登录

    Args:
        request: 登录请求（包含微信code）
        db: 数据库会话

    Returns:
        登录响应（token和用户信息）
    """
    auth_service = AuthService(db)
    try:
        result = await auth_service.wechat_login(request.code)
        return Response.success(data=result)
    except ValueError as e:
        return Response.error(code=1001, msg=str(e))
    except Exception as e:
        return Response.error(code=1002, msg=f"登录失败: {str(e)}")


@router.post("/account-login")
async def account_login(request: AccountLoginRequest, db: Session = Depends(get_db)):
    """
    账号密码登录

    Args:
        request: 账号登录请求（用户名/手机号 + 密码）
        db: 数据库会话

    Returns:
        登录响应（token和用户信息）
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.account_login(request.username, request.password)
        return Response.success(data=result)
    except ValueError as e:
        return Response.error(code=1001, msg=str(e))
    except Exception as e:
        return Response.error(code=1002, msg=f"登录失败: {str(e)}")


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    phone: str = None


@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    注册账号

    Args:
        request: 注册请求
        db: 数据库会话

    Returns:
        注册结果
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.register(request.username, request.password, request.phone)
        return Response.success(data=result)
    except ValueError as e:
        return Response.error(code=1001, msg=str(e))
    except Exception as e:
        return Response.error(code=1002, msg=f"注册失败: {str(e)}")


class SmsCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str
    scene: str = "login"  # register, reset, login


@router.post("/sms-code")
async def send_sms_code(request: SmsCodeRequest, db: Session = Depends(get_db)):
    """
    发送短信验证码

    Args:
        request: 发送请求
        db: 数据库会话

    Returns:
        发送结果
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.send_sms_code(request.phone, request.scene)
        return Response.success(data=result)
    except ValueError as e:
        return Response.error(code=1001, msg=str(e))
    except Exception as e:
        return Response.error(code=1002, msg=f"发送失败: {str(e)}")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    phone: str
    code: str
    password: str


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    重置密码

    Args:
        request: 重置请求
        db: 数据库会话

    Returns:
        重置结果
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.reset_password(request.phone, request.code, request.password)
        return Response.success(data=result)
    except ValueError as e:
        return Response.error(code=1001, msg=str(e))
    except Exception as e:
        return Response.error(code=1002, msg=f"重置失败: {str(e)}")
