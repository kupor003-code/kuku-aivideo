"""镜头生成API端点 - 支持镜头级别的图片生成控制"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import asyncio
import logging

from app.models.project import Project
from app.models.canvas_node import CanvasNode
from app.services.alibaba_image_service import get_alibaba_image_service
from app.db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# 存储镜头生成任务状态（生产环境应使用Redis）
_shot_generation_tasks: dict = {}


@router.post("/generate")
async def generate_shot_image(
    project_id: str,
    shot_number: int,
    shot_description: str,
    prompt: str,
    size: str = "1024*1024",
    n: int = 3,
    seed: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    为单个镜头生成图片

    Args:
        project_id: 项目ID
        shot_number: 镜头编号
        shot_description: 镜头描述
        prompt: 提示词
        size: 图片尺寸
        n: 生成数量
        seed: 随机种子
        db: 数据库会话

    Returns:
        生成任务信息
    """
    try:
        # 验证项目存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 创建镜头生成任务ID
        shot_gen_id = str(uuid.uuid4())
        shot_id = f"shot_{project_id}_{shot_number}"

        # 生成增强的提示词
        enhanced_prompt = f"{prompt}\n\n镜头描述: {shot_description}\n\n专业电影级分镜，高画质，细节丰富"

        # 调用图片生成服务
        image_service = get_alibaba_image_service()
        task_result = await image_service.generate_image(
            prompt=enhanced_prompt,
            size=size,
            n=n,
            seed=seed
        )

        # 保存任务状态
        _shot_generation_tasks[shot_gen_id] = {
            "shot_gen_id": shot_gen_id,
            "shot_id": shot_id,
            "shot_number": shot_number,
            "project_id": project_id,
            "status": "PENDING",
            "task_id": task_result.get("task_id"),
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
        }

        # 启动后台任务监控生成进度
        asyncio.create_task(monitor_shot_generation(shot_gen_id, task_result.get("task_id")))

        return {
            "shot_gen_id": shot_gen_id,
            "shot_id": shot_id,
            "shot_number": shot_number,
            "status": "PENDING",
            "task_id": task_result.get("task_id"),
            "message": "镜头生成任务已启动"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动镜头生成失败: {str(e)}")


@router.get("/{shot_gen_id}/status")
async def get_shot_generation_status(shot_gen_id: str):
    """
    获取镜头生成状态

    Args:
        shot_gen_id: 镜头生成任务ID

    Returns:
        任务状态
    """
    task = _shot_generation_tasks.get(shot_gen_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "shot_gen_id": task["shot_gen_id"],
        "shot_id": task["shot_id"],
        "shot_number": task["shot_number"],
        "status": task["status"],
        "progress": task.get("progress", 0),
        "error": task.get("error"),
        "image_ids": task.get("image_ids", []),
        "image_urls": task.get("image_urls", []),
        "seed": task.get("seed"),
    }


@router.post("/{shot_id}/pause")
async def pause_shot_generation(shot_id: str):
    """
    暂停镜头生成

    Args:
        shot_id: 镜头ID

    Returns:
        操作结果
    """
    # 查找对应的活动任务
    task = None
    for shot_gen_id, task_data in _shot_generation_tasks.items():
        if task_data.get("shot_id") == shot_id and task_data.get("status") == "GENERATING":
            task = task_data
            break

    if not task:
        raise HTTPException(status_code=404, detail="未找到进行中的生成任务")

    # 更新状态为暂停
    task["status"] = "PAUSED"
    task["paused_at"] = datetime.utcnow().isoformat()

    return {"message": "镜头生成已暂停", "shot_id": shot_id}


@router.post("/{shot_id}/resume")
async def resume_shot_generation(shot_id: str, background_tasks: BackgroundTasks):
    """
    继续镜头生成

    Args:
        shot_id: 镜头ID
        background_tasks: 后台任务

    Returns:
        操作结果
    """
    # 查找对应的活动任务
    task = None
    for shot_gen_id, task_data in _shot_generation_tasks.items():
        if task_data.get("shot_id") == shot_id and task_data.get("status") == "PAUSED":
            task = task_data
            break

    if not task:
        raise HTTPException(status_code=404, detail="未找到暂停的生成任务")

    # 恢复生成
    task["status"] = "GENERATING"
    task["resumed_at"] = datetime.utcnow().isoformat()

    # 重新启动监控
    background_tasks.add_task(monitor_shot_generation(shot_gen_id, task.get("task_id")))

    return {"message": "镜头生成已继续", "shot_id": shot_id}


@router.get("/project/{project_id}")
async def list_project_shots(project_id: str, db: Session = Depends(get_db)):
    """
    列出项目的所有镜头生成任务

    Args:
        project_id: 项目ID
        db: 数据库会话

    Returns:
        镜头任务列表
    """
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 筛选该项目的所有镜头任务
    shots = []
    for shot_gen_id, task_data in _shot_generation_tasks.items():
        if task_data.get("project_id") == project_id:
            shots.append({
                "shot_gen_id": shot_gen_id,
                "shot_id": task_data.get("shot_id"),
                "shot_number": task_data.get("shot_number"),
                "status": task_data.get("status"),
                "progress": task_data.get("progress", 0),
                "created_at": task_data.get("created_at"),
            })

    # 按镜头编号排序
    shots.sort(key=lambda x: x.get("shot_number", 0))

    return {"shots": shots}


async def monitor_shot_generation(shot_gen_id: str, task_id: str):
    """
    监控镜头生成进度

    Args:
        shot_gen_id: 镜头生成任务ID
        task_id: 图片生成任务ID
    """
    db: Session = next(get_db())
    try:
        if shot_gen_id not in _shot_generation_tasks:
            return

        task = _shot_generation_tasks[shot_gen_id]
        task["status"] = "GENERATING"
        project_id = task.get("project_id")
        shot_number = task.get("shot_number")

        logger.info(f"[SHOT GEN] 开始监控镜头生成: shot_gen_id={shot_gen_id}, project_id={project_id}, shot_number={shot_number}")

        image_service = get_alibaba_image_service()

        # 等待生成完成，带进度回调
        def progress_callback(progress):
            if shot_gen_id in _shot_generation_tasks:
                _shot_generation_tasks[shot_gen_id]["progress"] = progress
                logger.info(f"[SHOT GEN] 进度更新: shot_gen_id={shot_gen_id}, progress={progress}%")

        result = await image_service.wait_for_completion(
            task_id=task_id,
            interval=3,
            timeout=300,
            callback=progress_callback
        )

        # 提取图片URL
        image_urls = image_service.get_image_url(result)

        logger.info(f"[SHOT GEN] 图片生成完成: shot_gen_id={shot_gen_id}, urls={image_urls}")

        # 更新任务状态
        if shot_gen_id in _shot_generation_tasks:
            seed = None
            if image_urls and result.get("output", {}).get("results"):
                seed = result["output"]["results"][0].get("seed")

            _shot_generation_tasks[shot_gen_id].update({
                "status": "COMPLETED",
                "progress": 100,
                "image_urls": image_urls,
                "image_ids": [str(uuid.uuid4()) for _ in image_urls],
                "completed_at": datetime.utcnow().isoformat(),
                "seed": seed,
            })

        # 🔧 修复: 更新Canvas节点的data.images字段
        if project_id and image_urls:
            try:
                storyboard_node = db.query(CanvasNode).filter(
                    CanvasNode.project_id == project_id,
                    CanvasNode.node_type == "storyboard"
                ).first()

                if storyboard_node:
                    # 获取当前的images数组
                    current_images = storyboard_node.data.get("images", [])

                    # 为每个图片URL创建图片对象
                    new_images = []
                    for idx, url in enumerate(image_urls):
                        new_images.append({
                            "id": str(uuid.uuid4()),
                            "url": url,
                            "shot_number": shot_number,
                            "created_at": datetime.utcnow().isoformat(),
                        })

                    # 更新images数组
                    storyboard_node.data = {
                        **storyboard_node.data,
                        "images": current_images + new_images,
                    }

                    db.commit()
                    logger.info(f"[SHOT GEN] ✅ Canvas节点已更新: node_id={storyboard_node.id}, 新增图片数={len(new_images)}")
                else:
                    logger.warning(f"[SHOT GEN] ⚠️ 未找到Storyboard节点: project_id={project_id}")

            except Exception as e:
                logger.error(f"[SHOT GEN] ❌ 更新Canvas节点失败: {str(e)}")
                db.rollback()

    except Exception as e:
        logger.error(f"[SHOT GEN] ❌ 镜头生成失败: shot_gen_id={shot_gen_id}, error={str(e)}")

        # 标记任务失败
        if shot_gen_id in _shot_generation_tasks:
            _shot_generation_tasks[shot_gen_id].update({
                "status": "FAILED",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat(),
            })
    finally:
        db.close()
