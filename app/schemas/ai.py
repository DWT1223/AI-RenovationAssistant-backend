"""
AI生成Schema
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class AIPlanRequest(BaseModel):
    """AI方案生成请求"""
    house_type: str = Field(..., description="户型格局：一居/两居/三居/公寓")
    area: Decimal = Field(..., gt=0, description="面积（平方米）")
    style: str = Field(..., description="装修风格")
    budget: str = Field(..., description="预算档位：5万以下/5-10万/10-20万/20万以上")
    population: int = Field(2, ge=1, description="常住人口")
    special_needs: Optional[str] = Field(None, description="特殊需求")


class AIRenderRequest(BaseModel):
    """AI渲染图生成请求"""
    house_img_url: str = Field(..., description="户型图URL")
    style: str = Field(..., description="装修风格")
    room: Optional[str] = Field("all", description="空间：all/客厅/卧室/厨房/卫生间")


class AIRecordResponse(BaseModel):
    """AI记录响应"""
    id: int
    user_id: int
    type: str  # plan/render
    # 渲染图相关
    source_img: Optional[str] = None
    prompt: Optional[str] = None
    analysis_result: Optional[str] = None
    generated_img: Optional[str] = None
    # 方案相关
    params: Optional[str] = None
    result: Optional[str] = None
    status: int  # 0生成中/1成功/2失败
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIRecordListResponse(BaseModel):
    """AI记录列表响应"""
    items: List[AIRecordResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AITaskResponse(BaseModel):
    """AI任务响应"""
    task_id: str
    status: str  # pending/processing/succeeded/failed
    result: Optional[str] = None
    error: Optional[str] = None


class AIRenderAnalysisRequest(BaseModel):
    """AI渲染图分析请求"""
    source_img: Optional[str] = Field(None, description="上传的户型图URL")
    prompt: Optional[str] = Field(None, description="生成的提示词")
    analysis_result: Optional[str] = Field(None, description="AI分析结果")
    style: str = Field(..., description="装修风格")
    room: Optional[str] = Field("all", description="空间类型")
    requirement: Optional[str] = Field(None, description="用户需求描述")
