"""
收藏Schema
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CollectBase(BaseModel):
    """收藏基础Schema"""
    target_type: str = Field(..., description="收藏对象类型：note/style")
    target_id: int = Field(..., description="收藏对象ID")


class CollectCreate(CollectBase):
    """收藏创建Schema"""
    pass


class CollectResponse(BaseModel):
    """收藏响应Schema"""
    id: int
    user_id: int
    target_type: str
    target_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CollectListResponse(BaseModel):
    """收藏列表响应"""
    items: List[dict]  # 包含收藏对象详情
    total: int
    page: int
    page_size: int
    pages: int
