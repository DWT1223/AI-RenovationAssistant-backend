"""
AI 问答对话路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.database import get_db
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionDetailResponse,
)
from app.utils.response import Response
from app.utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/chat", tags=["聊天"])


def _session_to_dict(session: ChatSession, message_count: Optional[int] = None) -> dict:
    """将会话 ORM 对象转 dict（含 message_count），通过 Pydantic 自动处理 datetime"""
    base = ChatSessionResponse.model_validate(session).model_dump(mode="json")
    base["message_count"] = message_count if message_count is not None else len(session.messages or [])
    return base


@router.post("/sessions")
async def create_session(
    data: ChatSessionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """创建新会话"""
    session = ChatSession(
        user_id=user_id,
        title=(data.title or "新对话")[:255],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return Response.success(data=_session_to_dict(session, message_count=0))


@router.get("/sessions")
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有会话（按更新时间倒序）"""
    base = db.query(ChatSession).filter(ChatSession.user_id == user_id)
    total = base.count()

    # 一次查询拿到每个会话的消息数
    count_subq = (
        db.query(
            ChatMessage.session_id,
            func.count(ChatMessage.id).label("cnt"),
        )
        .group_by(ChatMessage.session_id)
        .subquery()
    )

    sessions = (
        db.query(ChatSession, func.coalesce(count_subq.c.cnt, 0).label("msg_count"))
        .outerjoin(count_subq, ChatSession.id == count_subq.c.session_id)
        .filter(ChatSession.user_id == user_id)
        .order_by(desc(ChatSession.updated_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for s, cnt in sessions:
        d = _session_to_dict(s, message_count=int(cnt or 0))
        items.append(d)

    return Response.page(items=items, total=total, page=page, page_size=page_size)


@router.get("/sessions/{session_id}")
async def get_session_detail(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取会话详情（含全部消息）"""
    session = (
        db.query(ChatSession)
        .options(joinedload(ChatSession.messages))
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        return Response.error(code=1001, msg="会话不存在")

    detail = _session_to_dict(session, message_count=len(session.messages))
    detail["messages"] = [
        ChatMessageResponse.model_validate(m).model_dump(mode="json")
        for m in session.messages
    ]
    return Response.success(data=detail)


@router.put("/sessions/{session_id}")
async def update_session(
    session_id: int,
    data: ChatSessionUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """更新会话（目前仅支持修改标题）"""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        return Response.error(code=1001, msg="会话不存在")

    if data.title is not None:
        session.title = data.title[:255]
        db.commit()
        db.refresh(session)

    # 避免触发懒加载：直接传 0 作为 message_count
    return Response.success(data=_session_to_dict(session, message_count=0))


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """删除会话（级联删除消息）"""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        return Response.error(code=1001, msg="会话不存在")

    db.delete(session)
    db.commit()
    return Response.success(msg="删除成功")


@router.post("/sessions/{session_id}/messages")
async def add_message(
    session_id: int,
    data: ChatMessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """向会话添加一条消息（同步刷新会话的 updated_at）"""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        return Response.error(code=1001, msg="会话不存在")

    msg = ChatMessage(
        session_id=session_id,
        user_id=user_id,
        role=data.role,
        content=data.content,
    )
    db.add(msg)

    # 触发 updated_at 刷新（即使没有字段值变化）
    session.updated_at = func.now()
    db.commit()
    db.refresh(msg)

    return Response.success(data=ChatMessageResponse.model_validate(msg).model_dump(mode="json"))
