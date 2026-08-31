"""
装修笔记路由
"""
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database import get_db
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse
from app.utils.response import Response
from app.utils.dependencies import get_current_user_id, get_optional_user_id
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/notes", tags=["笔记"])


@router.get("")
async def get_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    stage: Optional[str] = None,
    is_public: Optional[int] = None,
    my_notes: bool = False,
    sort: Optional[str] = Query(None, description="排序字段: like_count/created_at"),
    user_id: Optional[int] = Depends(get_optional_user_id),
    db: Session = Depends(get_db)
):
    """
    获取笔记列表

    Args:
        page: 页码
        page_size: 每页数量
        category: 分类筛选
        stage: 阶段筛选
        is_public: 公开筛选
        my_notes: 是否只看我的笔记
        sort: 排序字段 (like_count/created_at)
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        笔记列表
    """
    if my_notes:
        if not user_id:
            return Response.error(code=401, msg="请先登录")
        query = db.query(Note).filter(Note.user_id == user_id)
    else:
        query = db.query(Note).filter(Note.is_public == 1, Note.status == 1)

    if category:
        query = query.filter(Note.category == category)
    if stage:
        query = query.filter(Note.stage == stage)
    if is_public is not None:
        query = query.filter(Note.is_public == is_public)

    total = query.count()

    # 排序
    if sort == "like_count":
        notes = query.order_by(desc(Note.like_count), desc(Note.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
    else:
        notes = query.order_by(desc(Note.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

    # 关联用户信息
    items = []
    for note in notes:
        note_dict = NoteResponse.model_validate(note).model_dump(mode='json')
        if note.user_id:
            user = db.query(User).filter(User.id == note.user_id).first()
            if user:
                note_dict["user_nickname"] = user.nickname
                note_dict["user_avatar"] = user.avatar
        items.append(note_dict)

    return Response.page(items=items, total=total, page=page, page_size=page_size)


@router.post("")
async def create_note(
    data: NoteCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    创建笔记

    Args:
        data: 笔记数据
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        创建的笔记
    """
    note = Note(
        user_id=user_id,
        title=data.title,
        content=data.content,
        images=data.images,
        category=data.category,
        stage=data.stage,
        is_public=data.is_public,
        status=data.status
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    return Response.success(data=NoteResponse.model_validate(note).model_dump(mode='json'))


@router.get("/{note_id}")
async def get_note(
    note_id: int,
    user_id: Optional[int] = Depends(get_optional_user_id),
    db: Session = Depends(get_db)
):
    """
    获取笔记详情

    Args:
        note_id: 笔记ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        笔记详情
    """
    from app.models.collect import Collect

    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        return Response.error(code=1001, msg="笔记不存在")

    # 检查访问权限
    if note.is_public == 0 and (not user_id or note.user_id != user_id):
        return Response.error(code=1002, msg="无权限访问")

    note_dict = NoteResponse.model_validate(note).model_dump(mode='json')

    # 关联用户信息
    if note.user_id:
        user = db.query(User).filter(User.id == note.user_id).first()
        if user:
            note_dict["user_nickname"] = user.nickname
            note_dict["user_avatar"] = user.avatar

    # 检查是否已收藏
    if user_id:
        collect = db.query(Collect).filter(
            Collect.user_id == user_id,
            Collect.target_type == "note",
            Collect.target_id == note_id
        ).first()
        note_dict["is_favorited"] = collect is not None
        note_dict["collect_id"] = collect.id if collect else None
    else:
        note_dict["is_favorited"] = False
        note_dict["collect_id"] = None

    return Response.success(data=note_dict)


@router.put("/{note_id}")
async def update_note(
    note_id: int,
    data: NoteUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新笔记

    Args:
        note_id: 笔记ID
        data: 更新数据
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        更新后的笔记
    """
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()

    if not note:
        return Response.error(code=1001, msg="笔记不存在")

    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    if data.images is not None:
        note.images = data.images
    if data.category is not None:
        note.category = data.category
    if data.stage is not None:
        note.stage = data.stage
    if data.is_public is not None:
        note.is_public = data.is_public
    if data.status is not None:
        note.status = data.status

    db.commit()
    db.refresh(note)

    return Response.success(data=NoteResponse.model_validate(note).model_dump(mode='json'))


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除笔记

    Args:
        note_id: 笔记ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        删除结果
    """
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()

    if not note:
        return Response.error(code=1001, msg="笔记不存在")

    db.delete(note)
    db.commit()

    return Response.success(msg="删除成功")


@router.post("/{note_id}/like")
async def toggle_like(
    note_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    点赞/取消点赞笔记

    Args:
        note_id: 笔记ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        操作结果
    """
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        return Response.error(code=1001, msg="笔记不存在")

    # TODO: 实现点赞逻辑（需要点赞记录表）
    # 这里简单模拟
    note.like_count += 1
    db.commit()

    return Response.success(data={"like_count": note.like_count})
