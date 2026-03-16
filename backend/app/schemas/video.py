"""视频生成相关Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List


class GenerateVideoRequest(BaseModel):
    """生成视频请求Schema"""
    prompt: str = Field(..., description="视频生成提示词")
    image_url: Optional[str] = Field(None, description="起始图片URL（可选，用于图生视频）")
    duration: int = Field(5, description="视频时长（秒）", ge=1, le=10)
    fps: int = Field(30, description="帧率", ge=15, le=60)
    project_id: Optional[str] = Field(None, description="项目ID（用于链式操作）")
    source_image_id: Optional[str] = Field(None, description="源图片ID（用于链式操作溯源）")


class GenerateVideoResponse(BaseModel):
    """生成视频响应Schema"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")


class VideoTaskStatus(BaseModel):
    """视频任务状态Schema"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    results: Optional[List[dict]] = Field(None, description="视频结果列表")
    progress: Optional[int] = Field(None, description="进度百分比")


class VideoResult(BaseModel):
    """视频结果Schema"""
    id: str = Field(..., description="视频ID")
    url: str = Field(..., description="视频URL")
    prompt: str = Field(..., description="提示词")
    duration: Optional[int] = Field(None, description="视频时长")


class RegenerateVideoRequest(BaseModel):
    """重新生成视频请求Schema"""
    video_id: str = Field(..., description="原视频ID")
    variations: int = Field(3, description="变体数量", ge=1, le=5)
    style_change: str = Field("slight", description="风格变化程度")


class OptimizeVideoPromptRequest(BaseModel):
    """优化视频提示词请求Schema"""
    prompt: str = Field(..., description="原始提示词")
    focus: str = Field("motion", description="优化重点")
