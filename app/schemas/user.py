"""
用户相关Schema
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """用户基础Schema"""
    username: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """用户创建Schema"""
    openid: Optional[str] = None


class UserUpdate(BaseModel):
    """用户更新Schema"""
    username: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    openid: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求"""
    code: str = Field(..., description="微信登录code")


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user: UserResponse
