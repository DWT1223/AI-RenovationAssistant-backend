"""
预算路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetWithStatsResponse
from app.services.stats_service import StatsService
from app.utils.response import Response
from app.utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/budget", tags=["预算"])


@router.get("")
async def get_budget(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取预算信息

    Args:
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        预算信息
    """
    stats_service = StatsService(db)
    budget_stats = stats_service.get_budget_with_stats(user_id)

    return Response.success(data=budget_stats)


@router.put("")
async def set_budget(
    data: BudgetCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    设置/更新预算

    Args:
        data: 预算数据
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        预算信息
    """
    # 查询或创建预算
    budget = db.query(Budget).filter(Budget.user_id == user_id).first()

    if not budget:
        budget = Budget(user_id=user_id)
        db.add(budget)

    budget.total_budget = data.total_budget
    budget.items = data.items

    db.commit()
    db.refresh(budget)

    # 获取统计信息
    stats_service = StatsService(db)
    budget_stats = stats_service.get_budget_with_stats(user_id)

    return Response.success(data=budget_stats)
