"""剧本分镜API端点 - 集成video-shot-agent"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.services.video_shot_service import get_video_shot_service
from app.models.project import Project
from app.models.canvas_node import CanvasNode
from app.db.database import get_db

router = APIRouter()


@router.post("/generate")
async def generate_script_storyboard(
    project_id: str,
    script_text: str,
    task_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    使用video-shot-agent生成分镜脚本

    Args:
        project_id: 项目ID
        script_text: 剧本文本
        task_id: 可选的任务ID
        db: 数据库会话

    Returns:
        分镜生成结果
    """
    try:
        # 验证项目存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 调用video-shot-agent服务
        service = get_video_shot_service()

        # 生成唯一任务ID
        if not task_id:
            task_id = f"{project_id}_{uuid.uuid4().hex[:8]}"

        # 生成分镜
        result = await service.generate_storyboard(
            script_text=script_text,
            task_id=task_id,
            max_fragment_duration=10,
        )

        # 转换为Canvas格式
        scenes = service.convert_to_canvas_format(result)

        # 更新或创建Storyboard Canvas节点
        storyboard_node = db.query(CanvasNode).filter(
            CanvasNode.project_id == project_id,
            CanvasNode.node_type == "storyboard"
        ).first()

        if storyboard_node:
            # 更新现有节点
            storyboard_node.data = {
                **storyboard_node.data,
                "total_scenes": len(scenes),
                "total_shots": sum(s["total_shots"] for s in scenes),
                "scenes": scenes,
                "script_text": script_text,
                "source": "video-shot-agent",
                "status": "completed",
            }
        else:
            # 创建新节点
            storyboard_node = CanvasNode(
                project_id=project_id,
                node_type="storyboard",
                position_x=400,
                position_y=200,
                data={
                    "label": "分镜",
                    "total_scenes": len(scenes),
                    "total_shots": sum(s["total_shots"] for s in scenes),
                    "scenes": scenes,
                    "images": [],
                    "script_text": script_text,
                    "source": "video-shot-agent",
                    "status": "completed",
                    "projectId": project_id,
                },
            )
            db.add(storyboard_node)

        db.commit()
        db.refresh(storyboard_node)

        return {
            "success": True,
            "task_id": task_id,
            "message": f"✅ 成功生成 {len(scenes)} 个场景的分镜",
            "total_scenes": len(scenes),
            "total_shots": sum(s["total_shots"] for s in scenes),
            "scenes": scenes,
            "node_id": storyboard_node.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成剧本分镜失败: {str(e)}")


@router.get("/status/{task_id}")
async def get_script_storyboard_status(task_id: str):
    """
    获取剧本分镜任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态
    """
    try:
        service = get_video_shot_service()
        status = await service.get_task_status(task_id)
        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")
