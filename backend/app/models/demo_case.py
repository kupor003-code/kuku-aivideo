"""
演示案例数据模型
用于保存真实生成的演示内容，供所有用户查看
"""

from sqlalchemy import Column, String, Text, Float, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class DemoCase(Base):
    """演示案例模型"""
    __tablename__ = "demo_cases"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)  # 案例标题
    description = Column(Text)  # 案例描述

    # 剧本信息
    script = Column(Text, nullable=False)  # 原始剧本
    total_duration = Column(Float)  # 总时长（秒）

    # 分镜数据（JSON格式）
    fragments = Column(JSON, nullable=False)  # 包含所有分镜、图片URL、视频URL

    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 统计信息
    total_images = Column(Integer, default=0)
    total_videos = Column(Integer, default=0)

    # 是否公开
    is_public = Column(Integer, default=1)  # 1: 公开, 0: 私有

    def __repr__(self):
        return f"<DemoCase(id={self.id}, title={self.title})>"
