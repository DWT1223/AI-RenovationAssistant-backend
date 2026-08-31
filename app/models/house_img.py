"""
户型图模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class HouseImg(Base):
    """户型图表"""
    __tablename__ = "house_img"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="户型图ID")
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    img_url = Column(String(255), nullable=False, comment="图片URL")
    img_type = Column(String(32), nullable=True, comment="分类：原始户型/改造户型/竣工户型/毛坯实拍")
    title = Column(String(128), nullable=True, comment="名称")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    user = relationship("User", backref="house_imgs")

    def __repr__(self):
        return f"<HouseImg(id={self.id}, user_id={self.user_id}, img_type={self.img_type})>"
