"""提示词Schema"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class PromptType(str, Enum):
    """提示词类型"""
    IMAGE = "image"
    VIDEO = "video"


class PromptSource(str, Enum):
    """提示词来源"""
    USER = "user"
    AI = "ai"
    OPTIMIZED = "optimized"


class PromptCreate(BaseModel):
    """创建提示词Schema"""
    project_id: str = Field(..., description="项目ID")
    type: PromptType = Field(..., description="提示词类型")
    content: str = Field(..., description="提示词内容")
    source: PromptSource = Field(default=PromptSource.USER, description="提示词来源")
    parent_id: Optional[str] = Field(None, description="父版本ID")
    metadata: Optional[Dict] = Field(default_factory=dict, description="元数据")


class PromptResponse(BaseModel):
    """提示词响应Schema"""
    id: str
    project_id: str
    type: PromptType
    content: str
    version: int
    parent_id: Optional[str]
    source: PromptSource
    meta: Dict
    created_at: datetime
