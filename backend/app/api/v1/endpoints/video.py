"""视频生成API端点"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.video import (
    GenerateVideoRequest,
    GenerateVideoResponse,
    RegenerateVideoRequest,
    OptimizeVideoPromptRequest,
    VideoTaskStatus,
)
from app.agents.manager import get_agent_manager
from app.services.alibaba_video_service import get_alibaba_video_service
from app.services.file_storage_service import file_storage_service
from app.db.database import get_db
from app.models.video_generation import VideoGeneration
import uuid
from typing import Dict
import httpx

router = APIRouter()

# 存储任务状态（生产环境应该使用Redis或数据库）
_task_store: Dict[str, Dict] = {}


@router.post("/generate", response_model=GenerateVideoResponse)
async def generate_video(request: GenerateVideoRequest, background_tasks: BackgroundTasks):
    """
    生成视频

    Args:
        request: 生成请求
        background_tasks: 后台任务

    Returns:
        任务信息
    """
    try:
        # 获取视频Agent
        agent_manager = get_agent_manager()
        video_agent = agent_manager.get_video_agent()

        # 生成视频任务
        result = await video_agent.generate_video(
            prompt=request.prompt,
            image_url=request.image_url,
            duration=request.duration,
            fps=request.fps,
        )

        task_id = result["task_id"]

        # 保存任务信息
        _task_store[task_id] = {
            "task_id": task_id,
            "prompt": request.prompt,
            "image_url": request.image_url,
            "duration": request.duration,
            "fps": request.fps,
            "project_id": request.project_id,
            "source_image_id": request.source_image_id,
            "status": "PENDING",
            "results": [],
        }

        # 启动后台任务等待完成
        background_tasks.add_task(wait_for_video_task, task_id)

        return GenerateVideoResponse(task_id=task_id, status="PENDING")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=VideoTaskStatus)
async def get_video_task_status(task_id: str):
    """
    查询视频任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态
    """
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return VideoTaskStatus(
        task_id=task["task_id"],
        status=task["status"],
        results=task.get("results"),
        progress=task.get("progress"),
    )


@router.post("/regenerate")
async def regenerate_video(request: RegenerateVideoRequest):
    """
    重新生成视频变体

    Args:
        request: 重新生成请求

    Returns:
        任务ID列表
    """
    try:
        # 获取原任务信息
        original_task = _task_store.get(request.video_id)
        if not original_task:
            raise HTTPException(status_code=404, detail="原视频不存在")

        # 获取视频Agent
        agent_manager = get_agent_manager()
        video_agent = agent_manager.get_video_agent()

        # 重新生成
        tasks = await video_agent.regenerate(
            original_prompt=original_task["prompt"],
            variations=request.variations,
            style_change=request.style_change,
        )

        task_ids = [task["task_id"] for task in tasks]

        # 保存新任务
        for task in tasks:
            _task_store[task["task_id"]] = {
                "task_id": task["task_id"],
                "prompt": original_task["prompt"],
                "status": "PENDING",
                "results": [],
            }

        return {"task_ids": task_ids, "count": len(task_ids)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-prompt")
async def optimize_video_prompt(request: OptimizeVideoPromptRequest):
    """
    优化视频提示词

    Args:
        request: 优化请求

    Returns:
        优化后的提示词
    """
    try:
        # 获取视频Agent
        agent_manager = get_agent_manager()
        video_agent = agent_manager.get_video_agent()

        # 优化提示词
        optimized = await video_agent.optimize_prompt(
            original_prompt=request.prompt,
            focus=request.focus,
        )

        return {"original": request.prompt, "optimized": optimized}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def wait_for_video_task(task_id: str):
    """
    后台任务：等待视频生成完成并保存到本地

    Args:
        task_id: 任务ID
    """
    from app.db.database import SessionLocal
    
    try:
        video_service = get_alibaba_video_service()

        # 等待任务完成
        result = await video_service.wait_for_completion(
            task_id=task_id,
            interval=5,
            timeout=600,  # 视频生成可能需要10分钟
        )

        # 提取视频结果（包含id和url）
        video_results = video_service.get_video_result(result)

        # 获取任务信息
        task_info = _task_store.get(task_id)
        if not task_info:
            return

        project_id = task_info.get("project_id")
        
        # 处理结果并保存到本地
        saved_results = []
        db = SessionLocal()
        
        try:
            for video_result in video_results:
                saved_result = await _save_video_result(
                    db=db,
                    task_id=task_id,
                    project_id=project_id,
                    video_id=video_result.get("id"),
                    video_url=video_result.get("url"),
                    prompt=task_info.get("prompt"),
                    source_image_id=task_info.get("source_image_id")
                )
                saved_results.append(saved_result)
        finally:
            db.close()

        # 更新任务状态
        if task_id in _task_store:
            _task_store[task_id]["status"] = "SUCCEEDED"
            _task_store[task_id]["results"] = saved_results
            _task_store[task_id]["progress"] = 100

    except Exception as e:
        # 标记任务失败
        if task_id in _task_store:
            _task_store[task_id]["status"] = "FAILED"
            _task_store[task_id]["error"] = str(e)
            print(f"视频生成任务失败: {str(e)}")


async def _save_video_result(
    db: Session,
    task_id: str,
    project_id: str,
    video_id: str,
    video_url: str,
    prompt: str,
    source_image_id: str = None
) -> Dict:
    """
    保存视频结果到本地并记录到数据库
    
    Args:
        db: 数据库会话
        task_id: 生成任务ID
        project_id: 项目ID
        video_id: 视频ID
        video_url: 视频URL
        prompt: 提示词
        source_image_id: 源图片ID
        
    Returns:
        保存结果
    """
    try:
        # 下载视频
        response = httpx.get(video_url, timeout=300)
        if response.status_code != 200:
            raise Exception(f"下载视频失败: HTTP {response.status_code}")
        video_data = response.content
        
        # 保存到本地
        if project_id:
            file_info = file_storage_service.save_video(
                project_id=project_id,
                video_url=video_url,
                video_id=video_id,
                video_data=video_data
            )
            
            # 如果没有 prompt_version_id，创建一个临时的或使用占位符
            # 这里先使用占位符，后续可以通过其他方式关联
            from app.models.prompt_version import PromptVersion
            
            # 尝试获取或创建 prompt_version
            prompt_version = db.query(PromptVersion).filter(
                PromptVersion.project_id == project_id
            ).first()
            
            if not prompt_version:
                # 如果没有任何 prompt_version，创建一个临时的
                prompt_version = PromptVersion(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    content=prompt,
                    source="auto_generated"
                )
                db.add(prompt_version)
                db.flush()
            
            # 保存到数据库
            db_video = VideoGeneration(
                id=str(uuid.uuid4()),
                project_id=project_id,
                task_id=task_id,
                video_url=video_url,
                video_file_path=file_info["local_path"],
                video_local_url=file_info["file_url"],
                prompt_version_id=prompt_version.id,
                status="COMPLETED",
                generation_params={
                    "prompt": prompt,
                    "source_image_id": source_image_id,
                    "duration": 5,
                    "fps": 30,
                }
            )
            db.add(db_video)
            db.commit()
            
            return {
                "id": db_video.id,
                "url": file_info["file_url"],
                "local_path": file_info["local_path"],
                "prompt": prompt,
            }
        else:
            # 没有项目ID，仅返回结果
            return {
                "id": video_id,
                "url": video_url,
                "prompt": prompt,
            }
    except Exception as e:
        print(f"保存视频结果失败: {str(e)}")
        return {
            "id": video_id,
            "url": video_url,
            "prompt": prompt,
            "error": str(e)
        }


@router.delete("/{video_id}")
async def delete_video_generation(
    video_id: str,
    db: Session = Depends(get_db),
):
    """删除视频生成任务"""
    try:
        video_generation = db.query(VideoGeneration).filter(
            VideoGeneration.id == video_id
        ).first()
        
        if not video_generation:
            raise HTTPException(status_code=404, detail="视频生成任务不存在")
        
        # 删除关联的数据
        db.delete(video_generation)
        db.commit()
        
        return {
            "message": "视频生成任务已删除",
            "video_id": video_id,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.delete("/projects/{project_id}/videos")
async def delete_all_videos_for_project(
    project_id: str,
    db: Session = Depends(get_db),
):
    """删除项目所有视频生成任务"""
    try:
        # 验证项目存在
        from app.models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 删除所有视频生成任务
        count = db.query(VideoGeneration).filter(
            VideoGeneration.project_id == project_id
        ).delete()
        
        db.commit()
        
        return {
            "message": f"已删除 {count} 个视频生成任务",
            "project_id": project_id,
            "deleted_count": count,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
