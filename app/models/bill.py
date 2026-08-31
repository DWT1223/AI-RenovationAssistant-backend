"""
账单模型
"""
from sqlalchemy import Column, BigInteger, String, DECIMAL, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Bill(Base):
    """账单表"""
    __tablename__ = "bill"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="账单ID")
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    category = Column(String(32), nullable=False, index=True, comment="消费分类：设计费/硬装/水电/瓷砖/家具/家电/软装/人工杂费")
    amount = Column(DECIMAL(12, 2), nullable=False, default=0, comment="金额")
    bill_date = Column(Date, nullable=False, index=True, comment="消费日期")
    remark = Column(String(255), nullable=True, comment="备注")
    voucher = Column(String(255), nullable=True, comment="凭证照片URL")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    user = relationship("User", backref="bills")

    def __repr__(self):
        return f"<Bill(id={self.id}, category={self.category}, amount={self.amount})>"
