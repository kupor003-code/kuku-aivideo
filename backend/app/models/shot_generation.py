"""镜头级别的图片生成任务模型"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class ShotGenerationStatus(str, enum.Enum):
    """镜头生成状态"""
    PENDING = "pending"           # 待生成
    GENERATING = "generating"     # 生成中
    PAUSED = "paused"            # 已暂停
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"            # 失败


class ShotGeneration(Base):
    """镜头级别的图片生成任务 - 支持暂停/继续"""

    __tablename__ = "shot_generations"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    
    # 关联信息
    storyboard_image_id = Column(String, ForeignKey("storyboard_images.id"), nullable=True)
    
    # 镜头信息
    shot_number = Column(Integer, nullable=False)  # 镜头序号
    shot_description = Column(String, nullable=False)  # 镜头描述
    
    # 生成参数
    prompt = Column(String, nullable=False)  # 生成提示词
    generation_params = Column(JSON, default=dict)  # 其他生成参数（size、style等）
    
    # 状态追踪
    status = Column(SQLEnum(ShotGenerationStatus), default=ShotGenerationStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    
    # 任务信息
    task_id = Column(String, nullable=True)  # 外部 API 任务ID
    error_message = Column(String, nullable=True)  # 错误信息
    
    # 暂停信息
    paused_at = Column(DateTime, nullable=True)  # 暂停时间
    paused_progress = Column(Integer, nullable=True)  # 暂停时的进度
    
    # 元数据
    meta = Column(JSON, default=dict)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)  # 开始生成时间
    completed_at = Column(DateTime, nullable=True)  # 完成时间
    
    # 关系
    project = relationship("Project")
    storyboard_image = relationship("StoryboardImage")
