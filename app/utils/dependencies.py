"""
依赖注入工具
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.jwt import JWTTools


async def get_current_user_id(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> int:
    """
    获取当前登录用户的ID（必须登录）

    Args:
        authorization: Authorization请求头
        db: 数据库会话

    Returns:
        用户ID

    Raises:
        HTTPException: 未授权
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 提取Token
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    # 验证Token
    payload = JWTTools.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user_id


async def get_optional_user_id(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[int]:
    """
    获取当前登录用户的ID（可选）

    Args:
        authorization: Authorization请求头
        db: 数据库会话

    Returns:
        用户ID或None
    """
    if not authorization:
        return None

    # 提取Token
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    try:
        payload = JWTTools.verify_token(token)
        if payload:
            return payload.get("user_id")
    except Exception:
        pass

    return None
