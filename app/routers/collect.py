"""
收藏路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database import get_db
from app.models.collect import Collect
from app.models.note import Note
from app.models.style import Style
from app.models.user import User
from app.schemas.collect import CollectCreate, CollectResponse
from app.utils.response import Response
from app.utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/collects", tags=["收藏"])


@router.get("")
async def get_collects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    target_type: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取收藏列表

    Args:
        page: 页码
        page_size: 每页数量
        target_type: 收藏类型筛选
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        收藏列表
    """
    query = db.query(Collect).filter(Collect.user_id == user_id)

    if target_type:
        query = query.filter(Collect.target_type == target_type)

    total = query.count()
    collects = query.order_by(desc(Collect.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # 获取收藏对象详情
    items = []
    for collect in collects:
        item = CollectResponse.model_validate(collect).model_dump(mode='json')

        if collect.target_type == "note":
            note = db.query(Note).filter(Note.id == collect.target_id).first()
            if note:
                # 获取用户信息
                user = db.query(User).filter(User.id == note.user_id).first() if note.user_id else None
                item["target_data"] = {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content[:100] if note.content else None,
                    "images": note.images,
                    "category": note.category,
                    "stage": note.stage,
                    "like_count": note.like_count,
                    "favorite_count": note.favorite_count,
                    "user_id": note.user_id,
                    "user_nickname": user.nickname if user else None,
                    "user_avatar": user.avatar if user else None,
                    "created_at": note.created_at.isoformat() if note.created_at else None
                }
        elif collect.target_type == "style":
            style = db.query(Style).filter(Style.id == collect.target_id).first()
            if style:
                item["target_data"] = {
                    "id": style.id,
                    "name": style.name,
                    "cover": style.cover,
                    "description": style.description
                }

        items.append(item)

    return Response.page(items=items, total=total, page=page, page_size=page_size)


@router.post("")
async def create_collect(
    data: CollectCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    添加收藏

    Args:
        data: 收藏数据
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        创建结果
    """
    # 检查是否已收藏
    existing = db.query(Collect).filter(
        Collect.user_id == user_id,
        Collect.target_type == data.target_type,
        Collect.target_id == data.target_id
    ).first()

    if existing:
        return Response.error(code=1001, msg="已收藏")

    collect = Collect(
        user_id=user_id,
        target_type=data.target_type,
        target_id=data.target_id
    )
    db.add(collect)

    # 更新笔记收藏数
    if data.target_type == "note":
        note = db.query(Note).filter(Note.id == data.target_id).first()
        if note:
            note.favorite_count += 1

    db.commit()
    db.refresh(collect)

    return Response.success(data=CollectResponse.model_validate(collect).model_dump(mode='json'))


@router.delete("/{collect_id}")
async def delete_collect(
    collect_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    取消收藏

    Args:
        collect_id: 收藏ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        删除结果
    """
    collect = db.query(Collect).filter(
        Collect.id == collect_id,
        Collect.user_id == user_id
    ).first()

    if not collect:
        return Response.error(code=1001, msg="收藏不存在")

    # 更新被收藏对象的收藏数
    if collect.target_type == "note":
        note = db.query(Note).filter(Note.id == collect.target_id).first()
        if note and note.favorite_count > 0:
            note.favorite_count -= 1

    db.delete(collect)
    db.commit()

    return Response.success(msg="取消收藏成功")
