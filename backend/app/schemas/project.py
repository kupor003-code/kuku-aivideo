"""项目Schema"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    """项目基础Schema"""
    title: str = Field(..., description="项目标题")
    description: Optional[str] = Field(None, description="项目描述")


class ProjectCreate(ProjectBase):
    """创建项目Schema"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目Schema - V2支持"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    canvas_data: Optional[Dict[str, List[Any]]] = Field(None, description="Canvas数据（节点和边）")
    metadata: Optional[Dict[str, Any]] = Field(None, description="项目元数据")


class ProjectResponse(ProjectBase):
    """项目响应Schema - V2支持"""
    id: str
    status: ProjectStatus
    canvas_data: Optional[Dict[str, List[Any]]] = None
    meta: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = Field(None, description="项目配置")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
