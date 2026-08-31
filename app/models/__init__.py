"""
数据库模型
"""
from app.models.user import User
from app.models.note import Note
from app.models.bill import Bill
from app.models.budget import Budget
from app.models.house_img import HouseImg
from app.models.style import Style
from app.models.collect import Collect
from app.models.ai_record import AIRecord

__all__ = [
    "User",
    "Note",
    "Bill",
    "Budget",
    "HouseImg",
    "Style",
    "Collect",
    "AIRecord"
]
