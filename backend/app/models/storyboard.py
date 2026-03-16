"""分镜图片模型"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class StoryboardImage(Base):
    """分镜图片模型 - V2架构"""

    __tablename__ = "storyboard_images"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)

    # V2更新：关联PromptVersion而不是Prompt
    prompt_version_id = Column(String, ForeignKey("prompt_versions.id"), nullable=False)

    # 图片信息
    url = Column(String, nullable=True)  # 图片URL（远程或本地）
    file_path = Column(String, nullable=True)  # 本地文件路径（相对于项目根目录）
    
    # 访问信息
    local_url = Column(String, nullable=True)  # 本地访问 URL（/api/v1/files/...）

    # 元数据（尺寸、生成参数等）
    meta = Column(JSON, default=dict)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="storyboard_images")
    prompt_version = relationship("PromptVersion")
    video_generations = relationship("VideoGeneration", back_populates="storyboard_image")
