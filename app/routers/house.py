"""
户型图路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database import get_db
from app.models.house_img import HouseImg
from app.schemas.house_img import HouseImgCreate, HouseImgUpdate, HouseImgResponse
from app.utils.response import Response
from app.utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/house-imgs", tags=["户型图"])


@router.get("")
async def get_house_imgs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    img_type: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取户型图列表

    Args:
        page: 页码
        page_size: 每页数量
        img_type: 图片类型筛选
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        户型图列表
    """
    query = db.query(HouseImg).filter(HouseImg.user_id == user_id)

    if img_type:
        query = query.filter(HouseImg.img_type == img_type)

    total = query.count()
    imgs = query.order_by(desc(HouseImg.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = [HouseImgResponse.model_validate(img).model_dump(mode='json') for img in imgs]

    return Response.page(items=items, total=total, page=page, page_size=page_size)


@router.post("")
async def create_house_img(
    data: HouseImgCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    添加户型图

    Args:
        data: 户型图数据
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        创建的户型图
    """
    house_img = HouseImg(
        user_id=user_id,
        img_url=data.img_url,
        img_type=data.img_type,
        title=data.title
    )
    db.add(house_img)
    db.commit()
    db.refresh(house_img)

    return Response.success(data=HouseImgResponse.model_validate(house_img).model_dump(mode='json'))


@router.put("/{img_id}")
async def update_house_img(
    img_id: int,
    data: HouseImgUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新户型图

    Args:
        img_id: 户型图ID
        data: 更新数据
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        更新后的户型图
    """
    house_img = db.query(HouseImg).filter(
        HouseImg.id == img_id,
        HouseImg.user_id == user_id
    ).first()

    if not house_img:
        return Response.error(code=1001, msg="户型图不存在")

    if data.img_url is not None:
        house_img.img_url = data.img_url
    if data.img_type is not None:
        house_img.img_type = data.img_type
    if data.title is not None:
        house_img.title = data.title

    db.commit()
    db.refresh(house_img)

    return Response.success(data=HouseImgResponse.model_validate(house_img).model_dump(mode='json'))


@router.delete("/{img_id}")
async def delete_house_img(
    img_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除户型图

    Args:
        img_id: 户型图ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        删除结果
    """
    house_img = db.query(HouseImg).filter(
        HouseImg.id == img_id,
        HouseImg.user_id == user_id
    ).first()

    if not house_img:
        return Response.error(code=1001, msg="户型图不存在")

    db.delete(house_img)
    db.commit()

    return Response.success(msg="删除成功")
