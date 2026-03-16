"""协调Agent相关Schema"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal


class CreationPlan(BaseModel):
    """创作计划Schema"""
    overview: str = Field(..., description="整体概述")
    steps: List[str] = Field(..., description="创作步骤列表")
    storyboard_prompts: List[str] = Field(default_factory=list, description="分镜提示词建议")
    video_prompts: List[str] = Field(default_factory=list, description="视频提示词建议")
    estimated_duration: str = Field(..., description="预计时长")


class WorkflowState(BaseModel):
    """工作流状态Schema"""
    current_step: Literal['input', 'planning', 'storyboard_prompts',
                          'generating_storyboard', 'video_prompts',
                          'generating_video', 'completed'] = Field(
        default='input', description="当前步骤"
    )
    plan: Optional[CreationPlan] = Field(None, description="创作计划")
    selected_storyboard_prompt: Optional[str] = Field(None, description="选定的分镜提示词")
    storyboard_images: List[str] = Field(default_factory=list, description="分镜图片URL列表")
    selected_video_prompt: Optional[str] = Field(None, description="选定的视频提示词")
    video_url: Optional[str] = Field(None, description="视频URL")


class CoordinatorChatRequest(BaseModel):
    """协调Agent对话请求Schema"""
    message: str = Field("", description="用户消息")
    project_id: str = Field(..., description="项目ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    workflow_state: Optional[WorkflowState] = Field(None, description="工作流状态")


class CoordinatorChatResponse(BaseModel):
    """协调Agent对话响应Schema"""
    message: str = Field(..., description="AI回复")
    workflow_state: WorkflowState = Field(..., description="更新后的工作流状态")
    suggestions: List[str] = Field(default_factory=list, description="建议操作")


class GeneratePlanRequest(BaseModel):
    """生成创作计划请求Schema"""
    user_input: str = Field(..., description="用户的创意输入", min_length=1)
    project_id: str = Field(..., description="项目ID")


class GeneratePlanResponse(BaseModel):
    """生成创作计划响应Schema"""
    plan: CreationPlan = Field(..., description="生成的创作计划")


class RefinePromptRequest(BaseModel):
    """优化提示词请求Schema"""
    original_prompt: str = Field(..., description="原始提示词")
    user_feedback: str = Field(..., description="用户反馈")
    prompt_type: Literal['storyboard', 'video'] = Field(
        ..., description="提示词类型"
    )


class RefinePromptResponse(BaseModel):
    """优化提示词响应Schema"""
    refined_prompt: str = Field(..., description="优化后的提示词")


class GenerateStoryboardImagesRequest(BaseModel):
    """生成分镜图片请求Schema"""
    prompts: List[str] = Field(..., description="分镜提示词列表")
    project_id: str = Field(..., description="项目ID")
    size: str = Field(default="1024*1024", description="图片尺寸")


class GenerateStoryboardImagesResponse(BaseModel):
    """生成分镜图片响应Schema"""
    task_ids: List[str] = Field(..., description="图片生成任务ID列表")
    status: str = Field(..., description="任务状态")
