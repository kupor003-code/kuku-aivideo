"""Workflow Edge 模型 - 工作流边（连接关系）"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class EdgeType(str, enum.Enum):
    """边类型"""
    DATA_FLOW = "data_flow"         # 数据流（一个节点的输出作为另一个节点的输入）
    DEPENDENCY = "dependency"        # 依赖关系（必须等前一个节点完成）
    CONTROL_FLOW = "control_flow"    # 控制流（条件分支）
    SEQUENCE = "sequence"            # 顺序关系（按顺序执行）


class EdgeStatus(str, enum.Enum):
    """边状态"""
    ACTIVE = "active"               # 激活
    INACTIVE = "inactive"           # 未激活
    BLOCKED = "blocked"             # 阻塞（源节点未完成）
    COMPLETED = "completed"         # 已完成（数据已传递）


class WorkflowEdge(Base):
    """
    Workflow Edge 模型 - 工作流节点之间的连接关系

    这个模型定义了 Canvas 上节点之间的边（连接），
    用于工作流执行时的依赖管理和数据流控制。
    """

    __tablename__ = "workflow_edges"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)

    # 边的基本信息
    edge_type = Column(SQLEnum(EdgeType), nullable=False, default=EdgeType.DATA_FLOW)
    status = Column(SQLEnum(EdgeStatus), nullable=False, default=EdgeStatus.ACTIVE)

    # 源节点和目标节点
    source_node_id = Column(String, ForeignKey("canvas_nodes.id"), nullable=False)
    target_node_id = Column(String, ForeignKey("canvas_nodes.id"), nullable=False)

    # 条件表达式（用于控制流）
    # 例如：{"condition": "success", "operator": "==", "value": true}
    condition = Column(JSON, nullable=True)

    # 数据映射（用于数据流）
    # 例如：{"source_output": "prompt", "target_input": "script"}
    data_mapping = Column(JSON, nullable=True)

    # 元数据
    meta = Column(JSON, default=dict)

    # 排序字段（用于同一节点的多个输出边）
    order = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="workflow_edges")
    source_node = relationship(
        "CanvasNode",
        foreign_keys=[source_node_id],
        backref="outgoing_edges"
    )
    target_node = relationship(
        "CanvasNode",
        foreign_keys=[target_node_id],
        backref="incoming_edges"
    )

    def __repr__(self):
        return (
            f"<WorkflowEdge(id={self.id}, "
            f"type={self.edge_type}, "
            f"source={self.source_node_id}, "
            f"target={self.target_node_id})>"
        )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "edge_type": self.edge_type.value,
            "status": self.status.value,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "condition": self.condition,
            "data_mapping": self.data_mapping,
            "meta": self.meta,
            "order": self.order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
