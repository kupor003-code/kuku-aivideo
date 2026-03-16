"""项目模型"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    """项目状态"""
    DRAFT = "draft"                   # 草稿
    IN_PROGRESS = "in_progress"       # 进行中
    COMPLETED = "completed"           # 已完成
    ARCHIVED = "archived"             # 已归档


class Project(Base):
    """项目模型 - V2架构"""

    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)

    # V2新增：Canvas数据
    canvas_data = Column(JSON, default=dict)  # Canvas整体布局数据

    # V2新增：项目元数据（创意方向、风格等）
    meta = Column(JSON, default=dict)

    # 新增：项目配置
    config = Column(JSON, default=lambda: {
        "image_generation": {
            "ai_recommend_images": True,
            "default_images_per_scene": 3,
            "allow_manual_adjust": True,
            "min_images": 1,
            "max_images": 10,
        },
        "video_generation": {
            "resolution": "1080p",
            "duration": 3,
            "fps": 30,
            "style_strength": "medium",
        },
        "agent_config": {
            "enable_auto_generate": False,  # 默认不自动执行，需要用户确认
            "require_user_confirm": True,     # 每步需要用户确认
        },
    })

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # V2关系
    canvas_nodes = relationship("CanvasNode", back_populates="project", cascade="all, delete-orphan")
    workflow_edges = relationship("WorkflowEdge", back_populates="project", cascade="all, delete-orphan")
    prompt_versions = relationship("PromptVersion", back_populates="project", cascade="all, delete-orphan")
    video_generations = relationship("VideoGeneration", back_populates="project", cascade="all, delete-orphan")
    conversation_messages = relationship("ConversationMessage", back_populates="project", cascade="all, delete-orphan")
    storyboard_images = relationship("StoryboardImage", back_populates="project", cascade="all, delete-orphan")
    shot_generations = relationship("ShotGeneration", cascade="all, delete-orphan")
