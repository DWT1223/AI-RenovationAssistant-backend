"""
装修风格模型
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Style(Base):
    """装修风格表"""
    __tablename__ = "style"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="风格ID")
    name = Column(String(32), nullable=False, unique=True, comment="风格名称：现代简约/奶油风/轻奢/原木风/中式/极简/美式/ins风")
    cover = Column(String(255), nullable=True, comment="封面图URL")
    description = Column(Text, nullable=True, comment="风格介绍")
    color_scheme = Column(Text, nullable=True, comment="配色方案")
    material = Column(Text, nullable=True, comment="主材搭配要点")
    suitable = Column(Text, nullable=True, comment="适配户型")
    pros = Column(Text, nullable=True, comment="优点")
    cons = Column(Text, nullable=True, comment="缺点")
    sort = Column(Integer, default=0, nullable=False, comment="排序")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    def __repr__(self):
        return f"<Style(id={self.id}, name={self.name})>"
