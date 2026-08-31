"""
装修笔记模型
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, SmallInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Note(Base):
    """装修笔记表"""
    __tablename__ = "note"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="笔记ID")
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    title = Column(String(128), nullable=False, comment="标题")
    content = Column(Text, nullable=True, comment="正文内容")
    images = Column(Text, nullable=True, comment="图片URL列表JSON")
    category = Column(String(32), nullable=True, comment="分类：硬装/软装/水电/主材/避坑指南")
    stage = Column(String(32), nullable=True, comment="装修阶段：开工/水电/泥瓦/油漆/竣工")
    is_public = Column(SmallInteger, default=0, nullable=False, comment="是否公开：0私密/1公开")
    status = Column(SmallInteger, default=0, nullable=False, comment="状态：0草稿/1已发布")
    like_count = Column(Integer, default=0, nullable=False, comment="点赞数")
    favorite_count = Column(Integer, default=0, nullable=False, comment="收藏数")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    user = relationship("User", backref="notes")

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title}, user_id={self.user_id})>"
