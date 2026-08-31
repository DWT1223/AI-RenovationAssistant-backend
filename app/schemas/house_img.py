"""
户型图Schema
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class HouseImgBase(BaseModel):
    """户型图基础Schema"""
    img_url: str = Field(..., description="图片URL")
    img_type: Optional[str] = Field(None, description="分类：原始户型/改造户型/竣工户型/毛坯实拍")
    title: Optional[str] = Field(None, max_length=128, description="名称")


class HouseImgCreate(HouseImgBase):
    """户型图创建Schema"""
    pass


class HouseImgUpdate(BaseModel):
    """户型图更新Schema"""
    img_url: Optional[str] = None
    img_type: Optional[str] = None
    title: Optional[str] = Field(None, max_length=128)


class HouseImgResponse(HouseImgBase):
    """户型图响应Schema"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HouseImgListResponse(BaseModel):
    """户型图列表响应"""
    items: List[HouseImgResponse]
    total: int
    page: int
    page_size: int
    pages: int
