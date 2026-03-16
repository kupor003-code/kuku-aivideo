"""分镜管理API端点 - 支持镜头级别的生成和暂停"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.db.database import get_db
from app.models.project import Project
from app.models.shot_generation import ShotGeneration, ShotGenerationStatus
from app.schemas.storyboard_image_schema import StoryboardImageResponse

router = APIRouter()

# 临时存储正在生成的任务
_generating_tasks: Dict[str, Dict] = {}


@router.post("/shots/generate")
async def generate_shot_image(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    生成单个镜头的图片
    
    Args:
        request: {
            "project_id": "xxx",
            "shot_number": 1,
            "shot_description": "镜头描述",
            "prompt": "生成提示词",
            "size": "1024*1024",
            "n": 3,  # 生成数量
            "seed": 12345  # 可选：随机种子
        }
    """
    try:
        project_id = request.get("project_id")
        shot_number = request.get("shot_number")
        shot_description = request.get("shot_description")
        prompt = request.get("prompt")
        size = request.get("size", "1024*1024")
        n = request.get("n", 3)
        seed = request.get("seed")  # 可选的随机种子
        
        if not all([project_id, shot_number, prompt]):
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        # 验证项目存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 创建镜头生成记录
        shot_gen_id = str(uuid.uuid4())
        generation_params = {
            "size": size,
            "n": n,
        }
        if seed is not None:
            generation_params["seed"] = seed
            
        shot_generation = ShotGeneration(
            id=shot_gen_id,
            project_id=project_id,
            shot_number=shot_number,
            shot_description=shot_description,
            prompt=prompt,
            status=ShotGenerationStatus.GENERATING,
            generation_params=generation_params,
            started_at=datetime.utcnow(),
        )
        
        db.add(shot_generation)
        db.commit()
        db.refresh(shot_generation)
        
        # 启动后台生成任务
        background_tasks.add_task(
            _generate_shot_images,
            shot_gen_id,
            project_id,
            prompt,
            size,
            n,
            seed,
        )
        
        return {
            "shot_gen_id": shot_gen_id,
            "status": "GENERATING",
            "progress": 0,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/shots/{shot_gen_id}/pause")
async def pause_shot_generation(
    shot_gen_id: str,
    db: Session = Depends(get_db),
):
    """暂停镜头生成"""
    try:
        shot_generation = db.query(ShotGeneration).filter(
            ShotGeneration.id == shot_gen_id
        ).first()
        
        if not shot_generation:
            raise HTTPException(status_code=404, detail="镜头生成任务不存在")
        
        if shot_generation.status != ShotGenerationStatus.GENERATING:
            raise HTTPException(status_code=400, detail="只能暂停正在生成的任务")
        
        # 更新状态
        shot_generation.status = ShotGenerationStatus.PAUSED
        shot_generation.paused_at = datetime.utcnow()
        shot_generation.paused_progress = shot_generation.progress
        
        db.commit()
        db.refresh(shot_generation)
        
        return {
            "shot_gen_id": shot_gen_id,
            "status": shot_generation.status.value,
            "progress": shot_generation.progress,
            "paused_at": shot_generation.paused_at.isoformat(),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"暂停失败: {str(e)}")


@router.post("/shots/{shot_gen_id}/resume")
async def resume_shot_generation(
    shot_gen_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """继续镜头生成"""
    try:
        shot_generation = db.query(ShotGeneration).filter(
            ShotGeneration.id == shot_gen_id
        ).first()
        
        if not shot_generation:
            raise HTTPException(status_code=404, detail="镜头生成任务不存在")
        
        if shot_generation.status != ShotGenerationStatus.PAUSED:
            raise HTTPException(status_code=400, detail="只能继续暂停的任务")
        
        # 更新状态
        shot_generation.status = ShotGenerationStatus.GENERATING
        shot_generation.paused_at = None
        
        db.commit()
        
        # 继续后台生成任务
        background_tasks.add_task(
            _generate_shot_images,
            shot_gen_id,
            shot_generation.project_id,
            shot_generation.prompt,
            shot_generation.generation_params.get("size", "1024*1024"),
            shot_generation.generation_params.get("n", 3),
            shot_generation.generation_params.get("seed"),
        )
        
        return {
            "shot_gen_id": shot_gen_id,
            "status": ShotGenerationStatus.GENERATING.value,
            "progress": shot_generation.progress,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"继续失败: {str(e)}")


@router.get("/shots/{shot_gen_id}/status")
async def get_shot_generation_status(
    shot_gen_id: str,
    db: Session = Depends(get_db),
):
    """获取镜头生成状态"""
    try:
        shot_generation = db.query(ShotGeneration).filter(
            ShotGeneration.id == shot_gen_id
        ).first()
        
        if not shot_generation:
            raise HTTPException(status_code=404, detail="镜头生成任务不存在")
        
        result = {
            "shot_gen_id": shot_gen_id,
            "status": shot_generation.status.value,
            "progress": shot_generation.progress,
            "shot_number": shot_generation.shot_number,
            "shot_description": shot_generation.shot_description,
        }
        
        if shot_generation.storyboard_image_id:
            result["image_id"] = shot_generation.storyboard_image_id
        
        if shot_generation.error_message:
            result["error"] = shot_generation.error_message
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/projects/{project_id}/shots")
async def get_project_shots(
    project_id: str,
    db: Session = Depends(get_db),
):
    """获取项目所有镜头生成任务"""
    try:
        # 验证项目存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        shots = db.query(ShotGeneration).filter(
            ShotGeneration.project_id == project_id
        ).order_by(ShotGeneration.shot_number).all()
        
        result = []
        for shot in shots:
            result.append({
                "id": shot.id,
                "shot_number": shot.shot_number,
                "shot_description": shot.shot_description,
                "prompt": shot.prompt,
                "status": shot.status.value,
                "progress": shot.progress,
                "image_id": shot.storyboard_image_id,
                "error": shot.error_message,
            })
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.delete("/shots/{shot_gen_id}")
async def delete_shot_generation(
    shot_gen_id: str,
    db: Session = Depends(get_db),
):
    """删除镜头生成任务"""
    try:
        shot_generation = db.query(ShotGeneration).filter(
            ShotGeneration.id == shot_gen_id
        ).first()
        
        if not shot_generation:
            raise HTTPException(status_code=404, detail="镜头生成任务不存在")
        
        # 删除关联的数据
        db.delete(shot_generation)
        db.commit()
        
        return {
            "message": "镜头生成任务已删除",
            "shot_gen_id": shot_gen_id,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.delete("/projects/{project_id}/shots")
async def delete_all_shots_for_project(
    project_id: str,
    db: Session = Depends(get_db),
):
    """删除项目所有镜头生成任务"""
    try:
        # 验证项目存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 删除所有镜头生成任务
        count = db.query(ShotGeneration).filter(
            ShotGeneration.project_id == project_id
        ).delete()
        
        db.commit()
        
        return {
            "message": f"已删除 {count} 个镜头生成任务",
            "project_id": project_id,
            "deleted_count": count,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


async def _generate_shot_images(
    shot_gen_id: str,
    project_id: str,
    prompt: str,
    size: str,
    n: int,
    seed: int = None,
):
    """
    后台任务：生成镜头图片
    """
    from app.db.database import SessionLocal
    from app.services.alibaba_image_service import get_alibaba_image_service
    import requests
    from app.services.file_storage_service import file_storage_service
    from app.models.storyboard import StoryboardImage
    from app.models.prompt_version import PromptVersion
    
    db = SessionLocal()
    
    try:
        # 检查是否已暂停
        shot_gen = db.query(ShotGeneration).filter(
            ShotGeneration.id == shot_gen_id
        ).first()
        
        if not shot_gen:
            return
        
        # 获取图片生成服务
        image_service = get_alibaba_image_service()
        
        # 构建生成参数
        generate_kwargs = {
            "prompt": prompt,
            "size": size,
            "n": n,
        }
        if seed is not None:
            generate_kwargs["seed"] = seed
        
        # 生成图片
        result = await image_service.generate_image(**generate_kwargs)
        
        # 获取任务ID
        task_id = result.get("task_id")
        if not task_id:
            raise Exception("获取任务ID失败")
        
        # 更新状态
        shot_gen.task_id = task_id
        shot_gen.progress = 50
        db.commit()
        
        # 等待任务完成
        def progress_callback(progress: int):
            if db.is_active:
                shot_gen_update = db.query(ShotGeneration).filter(
                    ShotGeneration.id == shot_gen_id
                ).first()
                if shot_gen_update and shot_gen_update.status == ShotGenerationStatus.GENERATING:
                    shot_gen_update.progress = min(100, 50 + int(progress / 2))
                    db.commit()
        
        # 等待完成
        result = await image_service.wait_for_completion(
            task_id=task_id,
            interval=5,
            timeout=600,
            callback=progress_callback,
        )
        
        # 再次检查是否已暂停
        shot_gen_refresh = db.query(ShotGeneration).filter(
            ShotGeneration.id == shot_gen_id
        ).first()
        
        if shot_gen_refresh.status == ShotGenerationStatus.PAUSED:
            # 已暂停，不继续处理
            db.close()
            return
        
        # 获取图片结果
        image_results = image_service.get_image_result(result)
        
        if not image_results:
            raise Exception("生成失败：无图片结果")
        
        # 创建 PromptVersion（如果需要）
        prompt_version = db.query(PromptVersion).filter(
            PromptVersion.project_id == project_id
        ).first()
        
        if not prompt_version:
            prompt_version = PromptVersion(
                id=str(uuid.uuid4()),
                project_id=project_id,
                content=prompt,
                source="auto_generated",
            )
            db.add(prompt_version)
            db.flush()
        
        # 保存图片
        for idx, image_result in enumerate(image_results):
            image_url = image_result.get("url")
            if not image_url:
                continue
            
            # 下载图片
            response = requests.get(image_url, timeout=60)
            if response.status_code != 200:
                continue
            
            # 保存到本地
            image_id = str(uuid.uuid4())
            file_info = file_storage_service.save_image(
                project_id=project_id,
                image_url=image_url,
                image_id=image_id,
                image_data=response.content,
            )
            
            # 创建数据库记录
            storyboard_image = StoryboardImage(
                id=image_id,
                project_id=project_id,
                prompt_version_id=prompt_version.id,
                url=image_url,
                file_path=file_info["local_path"],
                local_url=file_info["file_url"],
                meta={
                    "prompt": prompt,
                    "shot_number": shot_gen_refresh.shot_number,
                    "shot_description": shot_gen_refresh.shot_description,
                    "index": idx,
                },
            )
            db.add(storyboard_image)
            db.flush()
            
            # 第一张图片关联到镜头生成任务
            if idx == 0:
                shot_gen_refresh.storyboard_image_id = image_id
        
        # 标记完成
        shot_gen_refresh.status = ShotGenerationStatus.COMPLETED
        shot_gen_refresh.progress = 100
        shot_gen_refresh.completed_at = datetime.utcnow()
        db.commit()
    
    except Exception as e:
        shot_gen_error = db.query(ShotGeneration).filter(
            ShotGeneration.id == shot_gen_id
        ).first()
        if shot_gen_error:
            shot_gen_error.status = ShotGenerationStatus.FAILED
            shot_gen_error.error_message = str(e)
            db.commit()
        print(f"生成镜头图片失败: {str(e)}")
    
    finally:
        db.close()
