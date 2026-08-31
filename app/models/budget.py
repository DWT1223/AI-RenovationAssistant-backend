"""
预算模型
"""
from sqlalchemy import Column, BigInteger, DECIMAL, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Budget(Base):
    """预算表"""
    __tablename__ = "budget"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="预算ID")
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True, comment="用户ID")
    total_budget = Column(DECIMAL(12, 2), nullable=False, default=0, comment="总预算")
    items = Column(Text, nullable=True, comment="分项预算JSON：[{\"category\":\"硬装\",\"amount\":50000}]")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    user = relationship("User", backref="budget", uselist=False)

    def __repr__(self):
        return f"<Budget(id={self.id}, user_id={self.user_id}, total_budget={self.total_budget})>"
