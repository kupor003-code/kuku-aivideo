"""分镜图片Schema"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class StoryboardImageCreate(BaseModel):
    """创建分镜图片Schema"""
    project_id: str = Field(..., description="项目ID")
    prompt_id: str = Field(..., description="提示词ID")
    url: Optional[str] = Field(None, description="图片URL")
    file_path: Optional[str] = Field(None, description="本地文件路径")
    metadata: Optional[Dict] = Field(default_factory=dict, description="元数据")


class StoryboardImageResponse(BaseModel):
    """分镜图片响应Schema"""
    id: str
    project_id: str
    prompt_id: str
    url: Optional[str]
    file_path: Optional[str]
    meta: Dict
    created_at: datetime
