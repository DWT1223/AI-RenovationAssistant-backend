"""
AI 问答对话 Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ---------- 会话 ----------

class ChatSessionCreate(BaseModel):
    """创建会话请求"""
    title: Optional[str] = Field("新对话", max_length=255, description="会话标题")


class ChatSessionUpdate(BaseModel):
    """更新会话请求"""
    title: Optional[str] = Field(None, max_length=255, description="会话标题")


class ChatSessionResponse(BaseModel):
    """会话响应（列表场景）"""
    id: int
    user_id: int
    title: str
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    """添加消息请求"""
    role: str = Field(..., pattern="^(user|assistant)$", description="角色：user/assistant")
    content: str = Field(..., min_length=1, description="消息内容")


class ChatMessageResponse(BaseModel):
    """消息响应"""
    id: int
    session_id: int
    user_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionDetailResponse(ChatSessionResponse):
    """会话详情（含消息列表）"""
    messages: List[ChatMessageResponse] = []
