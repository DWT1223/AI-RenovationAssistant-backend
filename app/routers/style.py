"""
装修风格路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc
from typing import Optional
from app.database import get_db
from app.models.style import Style
from app.models.collect import Collect
from app.schemas.style import StyleResponse, StyleListResponse
from app.utils.response import Response
from app.utils.dependencies import get_optional_user_id

router = APIRouter(prefix="/api/styles", tags=["装修风格"])


@router.get("")
async def get_styles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取装修风格列表

    Args:
        page: 页码
        page_size: 每页数量
        name: 风格名称筛选
        db: 数据库会话

    Returns:
        风格列表
    """
    query = db.query(Style)

    if name:
        query = query.filter(Style.name.like(f"%{name}%"))

    total = query.count()
    styles = query.order_by(asc(Style.sort), asc(Style.id)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = [StyleResponse.model_validate(s).model_dump(mode='json') for s in styles]

    return Response.page(items=items, total=total, page=page, page_size=page_size)


@router.get("/all")
async def get_all_styles(db: Session = Depends(get_db)):
    """
    获取所有装修风格（不分页）

    Args:
        db: 数据库会话

    Returns:
        所有风格列表
    """
    styles = db.query(Style).order_by(asc(Style.sort), asc(Style.id)).all()
    items = [StyleResponse.model_validate(s).model_dump(mode='json') for s in styles]

    return Response.success(data=items)


@router.get("/{style_id}")
async def get_style(
    style_id: int,
    user_id: Optional[int] = Depends(get_optional_user_id),
    db: Session = Depends(get_db)
):
    """
    获取风格详情

    Args:
        style_id: 风格ID
        user_id: 当前用户ID（可选）
        db: 数据库会话

    Returns:
        风格详情
    """
    style = db.query(Style).filter(Style.id == style_id).first()

    if not style:
        return Response.error(code=1001, msg="风格不存在")

    style_dict = StyleResponse.model_validate(style).model_dump(mode='json')

    # 检查是否已收藏
    if user_id:
        collect = db.query(Collect).filter(
            Collect.user_id == user_id,
            Collect.target_type == "style",
            Collect.target_id == style_id
        ).first()
        style_dict["is_favorited"] = collect is not None
        style_dict["collect_id"] = collect.id if collect else None
    else:
        style_dict["is_favorited"] = False
        style_dict["collect_id"] = None

    return Response.success(data=style_dict)
