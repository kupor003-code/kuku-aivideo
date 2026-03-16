"""提示词版本模型"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Integer, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class PromptSource(str, enum.Enum):
    """提示词来源"""
    USER = "user"           # 用户输入
    AI_DIRECTOR = "ai_director"      # AI导演生成
    AI_PRODUCER = "ai_producer"      # AI制片优化
    AI_ORCHESTRATOR = "ai_orchestrator"  # AI总控生成
    OPTIMIZED = "optimized"  # 优化后的


class PromptVersion(Base):
    """提示词版本模型 - 支持版本链管理"""

    __tablename__ = "prompt_versions"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    canvas_node_id = Column(String, ForeignKey("canvas_nodes.id"), nullable=True)

    # 提示词内容
    content = Column(Text, nullable=False)

    # 版本信息
    version = Column(Integer, default=1)
    parent_version_id = Column(String, ForeignKey("prompt_versions.id"), nullable=True)

    # 来源信息
    source = Column(SQLEnum(PromptSource), default=PromptSource.USER)
    agent_type = Column(String, nullable=True)  # orchestrator, director, producer等

    # 上下文信息
    context = Column(JSON, default=dict)  # 生成上下文（用户需求、创意方向等）

    # 元数据
    meta = Column(JSON, default=dict)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="prompt_versions")
    canvas_node = relationship("CanvasNode")
    parent = relationship("PromptVersion", remote_side=[id], backref="children")
