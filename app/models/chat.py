"""
AI 问答对话模型
"""
from sqlalchemy import (
    Column, BigInteger, String, Text,
    DateTime, ForeignKey, Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ChatSession(Base):
    """AI 问答会话表"""
    __tablename__ = "chat_session"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="会话ID")
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属用户ID"
    )
    title = Column(String(255), nullable=False, default="新对话", comment="会话标题")
    created_at = Column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )

    messages = relationship(
        "ChatMessage",
        backref="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, title='{self.title}')>"


class ChatMessage(Base):
    """AI 问答消息表"""
    __tablename__ = "chat_message"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="消息ID")
    session_id = Column(
        BigInteger,
        ForeignKey("chat_session.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属会话ID"
    )
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID（冗余字段，便于按用户过滤）"
    )
    role = Column(
        String(16), nullable=False, comment="角色：user 用户 / assistant AI"
    )
    content = Column(
        Text(4294967295), nullable=False, comment="消息内容（LONGTEXT）"
    )
    created_at = Column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )

    __table_args__ = (
        Index("idx_chat_msg_session_created", "session_id", "created_at"),
        Index("idx_chat_msg_user", "user_id"),
    )

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role={self.role})>"
