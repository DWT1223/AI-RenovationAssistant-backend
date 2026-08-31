"""
账单路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from decimal import Decimal
from app.database import get_db
from app.models.bill import Bill
from app.schemas.bill import BillCreate, BillUpdate, BillResponse, BillStatsResponse
from app.services.stats_service import StatsService
from app.utils.response import Response
from app.utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/bills", tags=["账单"])


@router.get("")
async def get_bills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取账单列表

    Args:
        page: 页码
        page_size: 每页数量
        category: 分类筛选
        start_date: 开始日期
        end_date: 结束日期
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        账单列表
    """
    query = db.query(Bill).filter(Bill.user_id == user_id)

    if category:
        query = query.filter(Bill.category == category)
    if start_date:
        query = query.filter(Bill.bill_date >= start_date)
    if end_date:
        query = query.filter(Bill.bill_date <= end_date)

    total = query.count()
    bills = query.order_by(Bill.bill_date.desc(), Bill.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = [BillResponse.model_validate(b).model_dump(mode='json') for b in bills]

    return Response.page(items=items, total=total, page=page, page_size=page_size)


@router.post("")
async def create_bill(
    data: BillCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    创建账单

    Args:
        data: 账单数据
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        创建的账单
    """
    bill = Bill(
        user_id=user_id,
        category=data.category,
        amount=data.amount,
        bill_date=data.bill_date,
        remark=data.remark,
        voucher=data.voucher
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)

    return Response.success(data=BillResponse.model_validate(bill).model_dump(mode='json'))


@router.get("/{bill_id}")
async def get_bill(
    bill_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取账单详情

    Args:
        bill_id: 账单ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        账单详情
    """
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == user_id
    ).first()

    if not bill:
        return Response.error(code=1001, msg="账单不存在")

    return Response.success(data=BillResponse.model_validate(bill).model_dump(mode='json'))


@router.put("/{bill_id}")
async def update_bill(
    bill_id: int,
    data: BillUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新账单

    Args:
        bill_id: 账单ID
        data: 更新数据
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        更新后的账单
    """
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == user_id
    ).first()

    if not bill:
        return Response.error(code=1001, msg="账单不存在")

    if data.category is not None:
        bill.category = data.category
    if data.amount is not None:
        bill.amount = data.amount
    if data.bill_date is not None:
        bill.bill_date = data.bill_date
    if data.remark is not None:
        bill.remark = data.remark
    if data.voucher is not None:
        bill.voucher = data.voucher

    db.commit()
    db.refresh(bill)

    return Response.success(data=BillResponse.model_validate(bill).model_dump(mode='json'))


@router.delete("/{bill_id}")
async def delete_bill(
    bill_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除账单

    Args:
        bill_id: 账单ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        删除结果
    """
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == user_id
    ).first()

    if not bill:
        return Response.error(code=1001, msg="账单不存在")

    db.delete(bill)
    db.commit()

    return Response.success(msg="删除成功")


@router.get("/stats/summary")
async def get_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取账单统计

    Args:
        start_date: 开始日期
        end_date: 结束日期
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        统计数据
    """
    stats_service = StatsService(db)
    stats = stats_service.get_bill_stats(user_id, start_date, end_date)

    return Response.success(data=stats)
