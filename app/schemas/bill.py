"""
账单Schema
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


class BillBase(BaseModel):
    """账单基础Schema"""
    category: str = Field(..., description="消费分类")
    amount: Decimal = Field(..., ge=0, description="金额")
    bill_date: date = Field(..., description="消费日期")
    remark: Optional[str] = Field(None, max_length=255, description="备注")
    voucher: Optional[str] = None  # 凭证照片URL


class BillCreate(BillBase):
    """账单创建Schema"""
    pass


class BillUpdate(BaseModel):
    """账单更新Schema"""
    category: Optional[str] = None
    amount: Optional[Decimal] = Field(None, ge=0)
    bill_date: Optional[date] = None
    remark: Optional[str] = Field(None, max_length=255)
    voucher: Optional[str] = None


class BillResponse(BillBase):
    """账单响应Schema"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillListResponse(BaseModel):
    """账单列表响应"""
    items: List[BillResponse]
    total: int
    page: int
    page_size: int
    pages: int


class BillStatsResponse(BaseModel):
    """账单统计响应"""
    total_amount: Decimal  # 总金额
    total_count: int  # 账单数量
    category_stats: List[dict]  # 分类统计
    daily_stats: List[dict]  # 每日统计
    monthly_stats: List[dict]  # 每月统计
