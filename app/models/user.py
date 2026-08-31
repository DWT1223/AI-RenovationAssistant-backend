"""
用户模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    openid = Column(String(64), unique=True, nullable=True, index=True, comment="微信openid")
    username = Column(String(64), unique=True, nullable=True, index=True, comment="用户名")
    password = Column(String(64), nullable=True, comment="密码哈希")
    nickname = Column(String(64), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    phone = Column(String(20), nullable=True, comment="手机号")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, nickname={self.nickname})>"
