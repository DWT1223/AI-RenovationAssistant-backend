"""
账单统计服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import date, datetime
from decimal import Decimal
from app.models.bill import Bill
from app.models.budget import Budget


class StatsService:
    """账单统计服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_bill_stats(
        self,
        user_id: int,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """
        获取账单统计

        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            统计数据
        """
        query = self.db.query(Bill).filter(Bill.user_id == user_id)

        if start_date:
            query = query.filter(Bill.bill_date >= start_date)
        if end_date:
            query = query.filter(Bill.bill_date <= end_date)

        # 总金额和总数量
        total = query.count()
        total_amount = query.with_entities(
            func.coalesce(func.sum(Bill.amount), 0)
        ).scalar()

        # 分类统计
        category_stats = self.db.query(
            Bill.category,
            func.sum(Bill.amount).label("amount"),
            func.count(Bill.id).label("count")
        ).filter(
            Bill.user_id == user_id
        ).group_by(Bill.category).all()

        category_list = [
            {
                "category": stat[0],
                "amount": float(stat[1]) if stat[1] else 0,
                "count": stat[2]
            }
            for stat in category_stats
        ]

        # 每日统计
        daily_stats = self.db.query(
            Bill.bill_date,
            func.sum(Bill.amount).label("amount")
        ).filter(
            Bill.user_id == user_id
        ).group_by(Bill.bill_date).order_by(
            Bill.bill_date.desc()
        ).limit(30).all()

        daily_list = [
            {
                "date": str(stat[0]),
                "amount": float(stat[1]) if stat[1] else 0
            }
            for stat in daily_stats
        ]

        # 每月统计
        monthly_stats = self.db.query(
            func.date_format(Bill.bill_date, "%Y-%m").label("month"),
            func.sum(Bill.amount).label("amount")
        ).filter(
            Bill.user_id == user_id
        ).group_by(
            func.date_format(Bill.bill_date, "%Y-%m")
        ).order_by(
            func.date_format(Bill.bill_date, "%Y-%m").desc()
        ).limit(12).all()

        monthly_list = [
            {
                "month": stat[0],
                "amount": float(stat[1]) if stat[1] else 0
            }
            for stat in monthly_stats
        ]

        return {
            "total_amount": float(total_amount) if total_amount else 0,
            "total_count": total,
            "category_stats": category_list,
            "daily_stats": daily_list,
            "monthly_stats": monthly_list
        }

    def get_budget_with_stats(self, user_id: int) -> Dict[str, Any]:
        """
        获取预算及消费统计

        Args:
            user_id: 用户ID

        Returns:
            预算及统计数据
        """
        # 获取预算
        budget = self.db.query(Budget).filter(Budget.user_id == user_id).first()

        # 计算已消费金额
        spent_amount = self.db.query(
            func.coalesce(func.sum(Bill.amount), 0)
        ).filter(Bill.user_id == user_id).scalar()

        # 各类别已消费
        category_spent = self.db.query(
            Bill.category,
            func.sum(Bill.amount).label("amount")
        ).filter(
            Bill.user_id == user_id
        ).group_by(Bill.category).all()

        category_list = [
            {
                "category": stat[0],
                "amount": float(stat[1]) if stat[1] else 0
            }
            for stat in category_spent
        ]

        if not budget:
            return {
                "has_budget": False,
                "total_budget": 0,
                "spent_amount": float(spent_amount) if spent_amount else 0,
                "remaining_amount": 0,
                "category_spent": category_list
            }

        total_budget = float(budget.total_budget) if budget.total_budget else 0
        spent = float(spent_amount) if spent_amount else 0

        return {
            "has_budget": True,
            "budget_id": budget.id,
            "total_budget": total_budget,
            "items": budget.items,
            "spent_amount": spent,
            "remaining_amount": total_budget - spent,
            "category_spent": category_list,
            "is_over_budget": spent > total_budget
        }
