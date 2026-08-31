"""
装修笔记Schema
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class NoteBase(BaseModel):
    """笔记基础Schema"""
    title: str = Field(..., max_length=128, description="标题")
    content: Optional[str] = None
    images: Optional[str] = None  # JSON字符串
    category: Optional[str] = Field(None, description="分类：硬装/软装/水电/主材/避坑指南")
    stage: Optional[str] = Field(None, description="装修阶段：开工/水电/泥瓦/油漆/竣工")
    is_public: int = Field(0, description="是否公开：0私密/1公开")
    status: int = Field(0, description="状态：0草稿/1已发布")


class NoteCreate(NoteBase):
    """笔记创建Schema"""
    pass


class NoteUpdate(BaseModel):
    """笔记更新Schema"""
    title: Optional[str] = Field(None, max_length=128)
    content: Optional[str] = None
    images: Optional[str] = None
    category: Optional[str] = None
    stage: Optional[str] = None
    is_public: Optional[int] = None
    status: Optional[int] = None


class NoteResponse(NoteBase):
    """笔记响应Schema"""
    id: int
    user_id: int
    like_count: int
    favorite_count: int
    created_at: datetime
    updated_at: datetime
    user_nickname: Optional[str] = None
    user_avatar: Optional[str] = None

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """笔记列表响应"""
    items: List[NoteResponse]
    total: int
    page: int
    page_size: int
    pages: int
