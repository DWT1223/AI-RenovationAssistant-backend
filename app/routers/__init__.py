"""
API路由
"""
from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
from app.routers.bill import router as bill_router
from app.routers.budget import router as budget_router
from app.routers.note import router as note_router
from app.routers.house import router as house_router
from app.routers.style import router as style_router
from app.routers.collect import router as collect_router
from app.routers.ai import router as ai_router
from app.routers.upload import router as upload_router
from app.routers.chat import router as chat_router

__all__ = [
    "auth_router",
    "user_router",
    "bill_router",
    "budget_router",
    "note_router",
    "house_router",
    "style_router",
    "collect_router",
    "ai_router",
    "upload_router",
    "chat_router"
]
