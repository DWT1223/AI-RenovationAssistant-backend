"""
AI路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import UploadFile, File, Form
from typing import Optional
import json
from app.database import get_db
from app.models.ai_record import AIRecord
from app.schemas.ai import (
    AIPlanRequest, AIRenderRequest, AIRecordResponse, AITaskResponse
)
from app.services.ai_service import AIService
from app.services.upload_service import UploadService
from app.utils.response import Response
from app.utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/plan")
async def generate_plan(
    data: AIPlanRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    生成装修方案

    Args:
        data: 方案生成参数
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        生成的方案
    """
    # 创建AI记录
    record = AIRecord(
        user_id=user_id,
        type="plan",
        params=json.dumps(data.model_dump(), ensure_ascii=False),
        status=0
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 调用AI服务生成方案
    ai_service = AIService()
    result = await ai_service.generate_plan(
        house_type=data.house_type,
        area=float(data.area),
        style=data.style,
        budget=data.budget,
        population=data.population,
        special_needs=data.special_needs
    )

    # 更新记录
    record.result = result
    record.status = 1
    db.commit()
    db.refresh(record)

    return Response.success(data={
        "record_id": record.id,
        "result": result
    })


@router.post("/render")
async def generate_render(
    house_img_url: str = Form(...),
    style: str = Form(...),
    room: str = Form("all"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    生成装修渲染图

    Args:
        house_img_url: 户型图URL
        style: 装修风格
        room: 空间类型
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        生成的任务ID
    """
    # 创建AI记录
    record = AIRecord(
        user_id=user_id,
        type="render",
        params=json.dumps({
            "house_img_url": house_img_url,
            "style": style,
            "room": room
        }, ensure_ascii=False),
        status=0
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 调用AI服务生成渲染图
    ai_service = AIService()
    result = await ai_service.generate_render(house_img_url, style, room)

    # 更新记录
    record.result = result
    record.status = 1
    db.commit()
    db.refresh(record)

    return Response.success(data={
        "record_id": record.id,
        "task_id": str(record.id),
        "result": result
    })


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    查询渲染任务状态

    Args:
        task_id: 任务ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        任务状态和结果
    """
    record = db.query(AIRecord).filter(
        AIRecord.id == int(task_id),
        AIRecord.user_id == user_id
    ).first()

    if not record:
        return Response.error(code=1001, msg="任务不存在")

    status_map = {
        0: "pending",
        1: "succeeded",
        2: "failed"
    }

    return Response.success(data={
        "task_id": str(record.id),
        "status": status_map.get(record.status, "unknown"),
        "result": record.result
    })


@router.get("/records")
async def get_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    record_type: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取AI生成历史

    Args:
        page: 页码
        page_size: 每页数量
        record_type: 记录类型
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        记录列表
    """
    query = db.query(AIRecord).filter(AIRecord.user_id == user_id)

    if record_type:
        query = query.filter(AIRecord.type == record_type)

    total = query.count()
    records = query.order_by(desc(AIRecord.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = [AIRecordResponse.model_validate(r).model_dump(mode='json') for r in records]

    return Response.page(items=items, total=total, page=page, page_size=page_size)


@router.post("/render/save")
async def save_render_record(
    record_type: Optional[str] = Form("render"),
    source_img: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
    analysis_result: Optional[str] = Form(None),
    generated_img: Optional[str] = Form(None),
    style: Optional[str] = Form(None),
    room: Optional[str] = Form(None),
    area: Optional[str] = Form(None),
    budget: Optional[str] = Form(None),
    population: Optional[str] = Form(None),
    requirement: Optional[str] = Form(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    保存渲染图生成记录

    Args:
        record_type: 记录类型：render-效果图/plan-装修方案
        source_img: 上传的户型图URL
        prompt: 生成的提示词
        analysis_result: AI分析结果
        generated_img: 生成的图片URL
        style: 装修风格
        room: 空间类型/户型
        area: 房屋面积
        budget: 预算
        population: 常住人口
        requirement: 用户需求描述
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        记录ID
    """
    record = AIRecord(
        user_id=user_id,
        type=record_type,
        source_img=source_img,
        prompt=prompt,
        analysis_result=analysis_result,
        generated_img=generated_img,
        params=json.dumps({
            "house_type": room,
            "area": area,
            "style": style,
            "budget": budget,
            "population": population,
            "requirement": requirement
        }, ensure_ascii=False),
        status=1 if generated_img else 0
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return Response.success(data={
        "record_id": record.id
    })


@router.post("/render/save-json")
async def save_render_record_json(
    record_type: Optional[str] = "render",
    source_img: Optional[str] = None,
    prompt: Optional[str] = None,
    analysis_result: Optional[str] = None,
    generated_img: Optional[str] = None,
    style: Optional[str] = None,
    room: Optional[str] = None,
    area: Optional[str] = None,
    budget: Optional[str] = None,
    population: Optional[str] = None,
    requirement: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    保存渲染图生成记录（JSON格式，支持大数据）

    Args:
        record_type: 记录类型：render-效果图/plan-装修方案
        source_img: 上传的户型图URL
        prompt: 生成的提示词
        analysis_result: AI分析结果
        generated_img: 生成的图片URL
        style: 装修风格
        room: 空间类型/户型
        area: 房屋面积
        budget: 预算
        population: 常住人口
        requirement: 用户需求描述
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        记录ID
    """
    record = AIRecord(
        user_id=user_id,
        type=record_type,
        source_img=source_img,
        prompt=prompt,
        analysis_result=analysis_result,
        generated_img=generated_img,
        params=json.dumps({
            "house_type": room,
            "area": area,
            "style": style,
            "budget": budget,
            "population": population,
            "requirement": requirement
        }, ensure_ascii=False),
        status=1 if generated_img else 0
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return Response.success(data={
        "record_id": record.id
    })
@router.get("/render/records")
async def get_render_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取渲染图生成历史

    Args:
        page: 页码
        page_size: 每页数量
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        记录列表
    """
    query = db.query(AIRecord).filter(
        AIRecord.user_id == user_id,
        AIRecord.type == "render"
    )

    total = query.count()
    records = query.order_by(desc(AIRecord.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = [AIRecordResponse.model_validate(r).model_dump(mode='json') for r in records]

    return Response.page(items=items, total=total, page=page, page_size=page_size)


@router.get("/render/records/{record_id}")
async def get_render_record_detail(
    record_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取渲染图记录详情

    Args:
        record_id: 记录ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        记录详情
    """
    record = db.query(AIRecord).filter(
        AIRecord.id == record_id,
        AIRecord.user_id == user_id,
        AIRecord.type == "render"
    ).first()

    if not record:
        return Response.error(code=1001, msg="记录不存在")

    return Response.success(data=AIRecordResponse.model_validate(record).model_dump(mode='json'))


@router.delete("/records/{record_id}")
async def delete_record(
    record_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除AI记录

    Args:
        record_id: 记录ID
        user_id: 当前用户ID
        db: 数据库会话

    Returns:
        删除结果
    """
    record = db.query(AIRecord).filter(
        AIRecord.id == record_id,
        AIRecord.user_id == user_id
    ).first()

    if not record:
        return Response.error(code=1001, msg="记录不存在")

    db.delete(record)
    db.commit()

    return Response.success(msg="删除成功")
