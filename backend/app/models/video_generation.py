"""视频生成记录模型"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class VideoGenerationStatus(str, enum.Enum):
    """视频生成状态"""
    PENDING = "pending"           # 等待中
    GENERATING = "generating"     # 生成中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"            # 失败


class VideoGeneration(Base):
    """视频生成记录模型"""

    __tablename__ = "video_generations"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    canvas_node_id = Column(String, ForeignKey("canvas_nodes.id"), nullable=True)

    # 关联数据
    storyboard_image_id = Column(String, ForeignKey("storyboard_images.id"), nullable=True)
    prompt_version_id = Column(String, ForeignKey("prompt_versions.id"), nullable=False)

    # 视频结果
    video_url = Column(String, nullable=True)  # 视频URL（远程或本地）
    thumbnail_url = Column(String, nullable=True)  # 缩略图URL
    
    # 本地文件信息
    video_file_path = Column(String, nullable=True)  # 本地文件路径（相对于项目根目录）
    video_local_url = Column(String, nullable=True)  # 本地访问 URL（/api/v1/files/...）

    # 生成参数
    generation_params = Column(JSON, default=dict)  # duration, fps, model等

    # 状态和进度
    status = Column(SQLEnum(VideoGenerationStatus), default=VideoGenerationStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(String, nullable=True)

    # 任务信息
    task_id = Column(String, nullable=True)  # 外部API任务ID

    # 元数据
    meta = Column(JSON, default=dict)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # 关系
    project = relationship("Project", back_populates="video_generations")
    canvas_node = relationship("CanvasNode")
    storyboard_image = relationship("StoryboardImage")
    prompt_version = relationship("PromptVersion")
