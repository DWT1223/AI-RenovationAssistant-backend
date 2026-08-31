"""
AI生成记录模型
"""
from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AIRecord(Base):
    """AI生成记录表"""
    __tablename__ = "ai_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    type = Column(String(16), nullable=False, comment="类型：plan方案/render渲染图")
    # 渲染图相关字段 - 使用 LONGTEXT 支持最长 4GB
    source_img = Column(Text(4294967295), nullable=True, comment="上传的户型图URL")
    prompt = Column(Text(4294967295), nullable=True, comment="生成提示词")
    analysis_result = Column(Text(4294967295), nullable=True, comment="AI分析结果")
    generated_img = Column(Text(4294967295), nullable=True, comment="生成的图片URL")
    # 方案相关字段
    params = Column(Text, nullable=True, comment="生成参数JSON：面积/户型/风格/预算")
    result = Column(Text, nullable=True, comment="生成结果：文本方案")
    status = Column(SmallInteger, default=0, nullable=False, comment="状态：0生成中/1成功/2失败")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    user = relationship("User", backref="ai_records")

    def __repr__(self):
        return f"<AIRecord(id={self.id}, user_id={self.user_id}, type={self.type}, status={self.status})>"
