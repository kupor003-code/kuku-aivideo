"""会话Schema"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class SessionCreate(BaseModel):
    """创建会话Schema"""
    project_id: str = Field(..., description="项目ID")
    agent_type: str = Field(..., description="Agent类型")


class MessageBase(BaseModel):
    """消息基础Schema"""
    role: str = Field(..., description="角色：user/assistant/system")
    content: str = Field(..., description="消息内容")


class MessageCreate(MessageBase):
    """创建消息Schema"""
    timestamp: Optional[str] = Field(None, description="时间戳")


class SessionResponse(BaseModel):
    """会话响应Schema"""
    id: str
    project_id: str
    agent_type: str
    messages: List[MessageBase]
    context: Dict
    created_at: datetime
    updated_at: datetime


class AppendMessageRequest(BaseModel):
    """追加消息请求Schema"""
    messages: List[MessageBase]
    context: Optional[Dict] = Field(default_factory=dict, description="上下文信息")


class UpdateSessionRequest(BaseModel):
    """更新会话请求Schema"""
    messages: Optional[List[MessageBase]] = None
    context: Optional[Dict] = None
