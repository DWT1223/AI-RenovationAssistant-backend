"""
用户路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.utils.response import Response
from app.utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.get("/profile")
async def get_profile(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息

    Args:
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        用户信息
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return Response.error(code=1001, msg="用户不存在")

    return Response.success(data=UserResponse.model_validate(user).model_dump(mode='json'))


@router.put("/profile")
async def update_profile(
    data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新用户信息

    Args:
        data: 更新数据
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        更新后的用户信息
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return Response.error(code=1001, msg="用户不存在")

    # 更新字段
    if data.nickname is not None:
        user.nickname = data.nickname
    if data.avatar is not None:
        user.avatar = data.avatar
    if data.phone is not None:
        user.phone = data.phone

    db.commit()
    db.refresh(user)

    return Response.success(data=UserResponse.model_validate(user).model_dump(mode='json'))
