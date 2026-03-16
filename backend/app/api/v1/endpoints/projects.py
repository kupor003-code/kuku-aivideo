"""项目管理API端点"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import uuid
import logging

from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.models.project import Project
from app.models.canvas_node import CanvasNode
from app.db.database import get_db
from app.services.file_storage_service import file_storage_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    创建项目

    Args:
        project: 项目创建请求
        db: 数据库会话

    Returns:
        创建的项目
    """
    try:
        # 生成项目ID
        project_id = str(uuid.uuid4())

        db_project = Project(
            id=project_id,
            title=project.title,
            description=project.description,
            status="draft",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        # 初始化项目文件夹
        file_storage_service.get_project_dir(project_id)
        file_storage_service.get_images_dir(project_id)
        file_storage_service.get_videos_dir(project_id)

        return db_project

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    获取项目列表

    Args:
        skip: 跳过数量
        limit: 限制数量
        db: 数据库会话

    Returns:
        项目列表
    """
    try:
        projects = db.query(Project).order_by(Project.updated_at.desc()).offset(skip).limit(limit).all()
        return projects

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """
    获取项目详情（动态从CanvasNode构建canvas_data）

    Args:
        project_id: 项目ID
        db: 数据库会话

    Returns:
        项目详情
    """
    try:
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 🔧 动态从CanvasNode表构建canvas_data，确保数据实时同步
        canvas_nodes = db.query(CanvasNode).filter(
            CanvasNode.project_id == project_id
        ).order_by(CanvasNode.created_at).all()

        # 构建节点和边
        flow_nodes = []
        flow_edges = []

        for node in canvas_nodes:
            # 构建React Flow节点
            flow_nodes.append({
                "id": node.id,
                "type": node.node_type,  # "prompt", "storyboard", "video"
                "position": {"x": node.position_x, "y": node.position_y},
                "data": node.data,
            })

            # 如果有父节点，创建边
            if node.parent_node_id:
                flow_edges.append({
                    "id": f"e-{node.parent_node_id}-{node.id}",
                    "source": node.parent_node_id,
                    "target": node.id,
                    "type": "smoothstep",
                })

        # 更新project的canvas_data（这样返回给前端的数据就是最新的）
        project.canvas_data = {
            "nodes": flow_nodes,
            "edges": flow_edges,
        }

        logger.debug(f"[PROJECT] 动态构建canvas_data: project_id={project_id}, nodes={len(flow_nodes)}, edges={len(flow_edges)}")

        return project

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目失败: {str(e)}")


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """
    更新项目

    Args:
        project_id: 项目ID
        project_update: 更新数据
        db: 数据库会话

    Returns:
        更新后的项目
    """
    try:
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 更新字段
        if project_update.title is not None:
            project.title = project_update.title
        if project_update.description is not None:
            project.description = project_update.description
        if project_update.status is not None:
            project.status = project_update.status
        if project_update.canvas_data is not None:
            project.canvas_data = project_update.canvas_data
        if project_update.metadata is not None:
            project.meta = project_update.metadata

        project.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(project)

        return project

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新项目失败: {str(e)}")


@router.delete("/{project_id}")
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    """
    删除项目（包括所有关联数据：会话、提示词、分镜图片、镜头生成任务、视频生成任务）

    Args:
        project_id: 项目ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 统计删除的相关数据
        from app.models.shot_generation import ShotGeneration
        from app.models.video_generation import VideoGeneration
        from app.models.conversation import ConversationMessage
        from app.models.storyboard import StoryboardImage
        
        shot_count = db.query(ShotGeneration).filter(
            ShotGeneration.project_id == project_id
        ).count()
        
        video_count = db.query(VideoGeneration).filter(
            VideoGeneration.project_id == project_id
        ).count()
        
        message_count = db.query(ConversationMessage).filter(
            ConversationMessage.project_id == project_id
        ).count()
        
        image_count = db.query(StoryboardImage).filter(
            StoryboardImage.project_id == project_id
        ).count()

        # 删除项目（级联删除会自动删除所有关联数据）
        db.delete(project)
        db.commit()
        
        # 删除项目文件夹
        file_storage_service.delete_project(project_id)

        return {
            "message": "项目已删除",
            "project_id": project_id,
            "deleted_items": {
                "shot_generation_tasks": shot_count,
                "video_generation_tasks": video_count,
                "conversation_messages": message_count,
                "storyboard_images": image_count,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除项目失败: {str(e)}")
