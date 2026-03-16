"""Canvas节点模型"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Integer, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class NodeType(str, enum.Enum):
    """节点类型"""
    PROMPT = "prompt"           # 提示词节点
    STORYBOARD = "storyboard"   # 分镜节点
    VIDEO = "video"             # 视频节点


class NodeStatus(str, enum.Enum):
    """节点状态"""
    DRAFT = "draft"             # 草稿
    GENERATING = "generating"   # 生成中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败


class CanvasNode(Base):
    """Canvas节点模型 - 核心工作流节点"""

    __tablename__ = "canvas_nodes"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)

    # 节点类型和状态
    node_type = Column(SQLEnum(NodeType), nullable=False)
    status = Column(SQLEnum(NodeStatus), default=NodeStatus.DRAFT)

    # 树状结构（父子关系）
    parent_node_id = Column(String, ForeignKey("canvas_nodes.id"), nullable=True)

    # Canvas布局位置
    position_x = Column(Float, default=0)
    position_y = Column(Float, default=0)

    # 节点数据（JSON格式，根据node_type存储不同数据）
    data = Column(JSON, default=dict)

    # 元数据
    meta = Column(JSON, default=dict)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="canvas_nodes")
    parent = relationship("CanvasNode", remote_side=[id], backref="children")
