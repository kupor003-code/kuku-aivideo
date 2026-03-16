"""分镜图片Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GenerateImageRequest(BaseModel):
    """生成图片请求Schema"""
    prompt: str = Field(..., description="图片提示词", min_length=1)
    size: str = Field("1024*1024", description="图片尺寸")
    n: int = Field(1, description="生成数量", ge=1, le=4)
    seed: Optional[int] = Field(None, description="随机种子")


class GenerateImageResponse(BaseModel):
    """生成图片响应Schema"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")


class ImageResult(BaseModel):
    """图片结果Schema"""
    id: str = Field(..., description="图片ID")
    url: str = Field(..., description="图片URL")
    prompt: str = Field(..., description="使用的提示词")


class RegenerateImageRequest(BaseModel):
    """重新生成图片请求Schema"""
    image_id: str = Field(..., description="原图片ID")
    variations: int = Field(3, description="变体数量", ge=1, le=5)
    style_change: str = Field("slight", description="风格变化程度")


class OptimizePromptRequest(BaseModel):
    """优化提示词请求Schema"""
    prompt: str = Field(..., description="原始提示词")
    focus: str = Field("quality", description="优化重点: quality/style/composition")


class ImageTaskStatus(BaseModel):
    """图片任务状态Schema"""
    task_id: str
    status: str
    results: Optional[List[ImageResult]] = None
    progress: Optional[int] = None
