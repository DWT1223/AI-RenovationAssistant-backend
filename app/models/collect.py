"""
收藏模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Collect(Base):
    """收藏表"""
    __tablename__ = "collect"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    target_type = Column(String(16), nullable=False, index=True, comment="收藏对象类型：note/style")
    target_id = Column(BigInteger, nullable=False, index=True, comment="收藏对象ID")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="收藏时间")

    # 关系
    user = relationship("User", backref="collects")

    # 唯一约束
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_target"),
    )

    def __repr__(self):
        return f"<Collect(id={self.id}, user_id={self.user_id}, target_type={self.target_type}, target_id={self.target_id})>"
