"""
预算Schema
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class BudgetItem(BaseModel):
    """预算项"""
    category: str
    amount: Decimal


class BudgetBase(BaseModel):
    """预算基础Schema"""
    total_budget: Decimal = Field(..., ge=0, description="总预算")
    items: Optional[str] = None  # JSON字符串


class BudgetCreate(BudgetBase):
    """预算创建Schema"""
    pass


class BudgetUpdate(BaseModel):
    """预算更新Schema"""
    total_budget: Optional[Decimal] = Field(None, ge=0)
    items: Optional[str] = None


class BudgetResponse(BudgetBase):
    """预算响应Schema"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetWithStatsResponse(BudgetResponse):
    """带统计的预算响应"""
    spent_amount: Decimal = Field(default=Decimal("0"))  # 已花费
    remaining_amount: Decimal = Field(default=Decimal("0"))  # 剩余
    category_spent: List[dict] = Field(default_factory=list)  # 各类别已花费
