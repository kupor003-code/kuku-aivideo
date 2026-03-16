"""对话消息模型"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class MessageRole(str, enum.Enum):
    """消息角色"""
    USER = "user"             # 用户
    ASSISTANT = "assistant"   # AI助手
    SYSTEM = "system"         # 系统消息


class ConversationMessage(Base):
    """对话消息模型 - AI导演团队对话记录"""

    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)

    # 消息基础信息
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Agent信息（当role=assistant时使用）
    agent_type = Column(String, nullable=True)  # orchestrator, director, producer等
    agent_name = Column(String, nullable=True)  # 显示名称：AI导演、AI制片等

    # 关联信息（连接消息与Canvas节点）
    related_node_id = Column(String, ForeignKey("canvas_nodes.id"), nullable=True)
    related_node_type = Column(String, nullable=True)  # prompt, storyboard, video

    # 元数据（包含动作、建议等）
    meta = Column(JSON, default=dict)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="conversation_messages")
    related_node = relationship("CanvasNode")
