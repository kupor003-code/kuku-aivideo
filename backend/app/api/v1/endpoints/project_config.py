"""项目配置API端点"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db.database import get_db
from app.models.project import Project

router = APIRouter()


@router.get("/{project_id}/config")
async def get_project_config(project_id: str, db: Session = Depends(get_db)):
    """
    获取项目配置

    Args:
        project_id: 项目ID
        db: 数据库会话

    Returns:
        项目配置
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    return {
        "project_id": project_id,
        "config": project.config or {},
    }


@router.put("/{project_id}/config")
async def update_project_config(
    project_id: str,
    config: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    更新项目配置

    Args:
        project_id: 项目ID
        config: 新的配置
        db: 数据库会话

    Returns:
        更新后的配置
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 更新配置
    project.config = config
    db.commit()
    db.refresh(project)

    return {
        "project_id": project_id,
        "config": project.config,
        "message": "配置已更新",
    }


@router.patch("/{project_id}/config")
async def patch_project_config(
    project_id: str,
    config_update: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    部分更新项目配置

    Args:
        project_id: 项目ID
        config_update: 要更新的配置部分
        db: 数据库会话

    Returns:
        更新后的完整配置
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 合并配置
    current_config = project.config or {}
    updated_config = {**current_config, **config_update}
    project.config = updated_config

    db.commit()
    db.refresh(project)

    return {
        "project_id": project_id,
        "config": project.config,
        "message": "配置已更新",
    }
