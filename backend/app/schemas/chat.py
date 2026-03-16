"""对话Schema"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Message(BaseModel):
    """消息Schema"""
    role: str = Field(..., description="角色：user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[str] = Field(None, description="时间戳")


class ChatRequest(BaseModel):
    """对话请求Schema"""
    message: str = Field(..., description="用户消息", min_length=1)
    session_id: Optional[str] = Field(None, description="会话ID")
    project_id: Optional[str] = Field(None, description="项目ID")
    context: Optional[Dict] = Field(default_factory=dict, description="上下文信息")


class ChatResponse(BaseModel):
    """对话响应Schema"""
    message: str = Field(..., description="AI回复")
    session_id: str = Field(..., description="会话ID")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="建议操作")


class GeneratePromptRequest(BaseModel):
    """生成提示词请求Schema"""
    prompt_type: str = Field(..., description="提示词类型：storyboard/video")
    session_id: Optional[str] = Field(None, description="会话ID")


class GeneratePromptResponse(BaseModel):
    """生成提示词响应Schema"""
    prompt: str = Field(..., description="生成的提示词")
    prompt_type: str = Field(..., description="提示词类型")
