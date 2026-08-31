"""
装修风格Schema
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class StyleBase(BaseModel):
    """风格基础Schema"""
    name: str = Field(..., max_length=32, description="风格名称")
    cover: Optional[str] = None  # 封面图URL
    description: Optional[str] = None  # 风格介绍
    color_scheme: Optional[str] = None  # 配色方案
    material: Optional[str] = None  # 主材搭配要点
    suitable: Optional[str] = None  # 适配户型
    pros: Optional[str] = None  # 优点
    cons: Optional[str] = None  # 缺点
    sort: int = Field(0, description="排序")


class StyleCreate(StyleBase):
    """风格创建Schema"""
    pass


class StyleUpdate(BaseModel):
    """风格更新Schema"""
    name: Optional[str] = Field(None, max_length=32)
    cover: Optional[str] = None
    description: Optional[str] = None
    color_scheme: Optional[str] = None
    material: Optional[str] = None
    suitable: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    sort: Optional[int] = None


class StyleResponse(StyleBase):
    """风格响应Schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StyleListResponse(BaseModel):
    """风格列表响应"""
    items: List[StyleResponse]
    total: int
    page: int
    page_size: int
    pages: int
