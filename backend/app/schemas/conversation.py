"""对话相关Schema"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    role: str = Field(..., description="角色: user, assistant, system")
    content: str = Field(..., description="消息内容")
    agent_type: Optional[str] = Field(None, description="Agent类型")
    agent_name: Optional[str] = Field(None, description="Agent显示名称")
    related_node_id: Optional[str] = Field(None, description="关联的Canvas节点ID")
    related_node_type: Optional[str] = Field(None, description="节点类型")
    meta: Optional[Dict[str, Any]] = Field(None, description="元数据")


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    project_id: str
    role: str
    content: str
    agent_type: Optional[str]
    agent_name: Optional[str]
    related_node_id: Optional[str]
    related_node_type: Optional[str]
    meta: Optional[Dict[str, Any]]
    created_at: str
