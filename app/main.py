"""
FastAPI应用入口
"""
from typing import Optional
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
import os
from loguru import logger

from app.config import get_settings
from app.database import init_db
from app.utils.dependencies import get_current_user_id, get_optional_user_id
from app.routers import (
    auth_router,
    user_router,
    bill_router,
    budget_router,
    note_router,
    house_router,
    style_router,
    collect_router,
    ai_router,
    upload_router
)

# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title="装修AI小程序后端API",
    description="基于FastAPI的装修AI助手后端服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置请求体最大大小为 50MB
app.state.max_body_size = 50 * 1024 * 1024

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 注册路由
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(bill_router)
app.include_router(budget_router)
app.include_router(note_router)
app.include_router(house_router)
app.include_router(style_router)
app.include_router(collect_router)
app.include_router(ai_router)
app.include_router(upload_router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("装修AI小程序后端服务启动中...")
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    logger.info("服务启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("装修AI小程序后端服务关闭中...")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "服务器内部错误",
            "data": None
        }
    )


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "装修AI小程序后端API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}
