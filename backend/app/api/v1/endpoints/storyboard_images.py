"""分镜图片管理API端点 - V2使用PromptVersion"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
import requests

from app.schemas.storyboard_image_schema import StoryboardImageCreate, StoryboardImageResponse
from app.models.storyboard import StoryboardImage as StoryboardImageModel
from app.models.project import Project
from app.models.prompt_version import PromptVersion as Prompt  # V2
from app.db.database import get_db
from app.services.file_storage_service import file_storage_service

router = APIRouter()


@router.post("/", response_model=StoryboardImageResponse)
async def create_storyboard_image(image: StoryboardImageCreate, db: Session = Depends(get_db)):
    """
    创建分镜图片记录

    Args:
        image: 分镜图片创建请求
        db: 数据库会话

    Returns:
        创建的分镜图片
    """
    try:
        # 验证项目是否存在
        project = db.query(Project).filter(Project.id == image.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 验证提示词是否存在
        prompt = db.query(Prompt).filter(Prompt.id == image.prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="提示词不存在")

        # 生成图片ID
        image_id = str(uuid.uuid4())
        
        # 如果有URL，尝试下载并保存到本地
        local_url = None
        file_path = image.file_path
        if image.url:
            try:
                response = requests.get(image.url, timeout=60)
                if response.status_code == 200:
                    image_data = response.content
                    file_info = file_storage_service.save_image(
                        project_id=image.project_id,
                        image_url=image.url,
                        image_id=image_id,
                        image_data=image_data
                    )
                    file_path = file_info["local_path"]
                    local_url = file_info["file_url"]
            except Exception as e:
                print(f"下载并保存图片失败: {str(e)}")
                # 继续处理，使用原始URL

        db_image = StoryboardImageModel(
            id=image_id,
            project_id=image.project_id,
            prompt_id=image.prompt_id,
            url=image.url,
            file_path=file_path,
            local_url=local_url,
            meta=image.metadata,
            created_at=datetime.utcnow(),
        )

        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return db_image

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建分镜图片失败: {str(e)}")


@router.get("/project/{project_id}", response_model=List[StoryboardImageResponse])
async def get_project_storyboard_images(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    获取项目的所有分镜图片

    Args:
        project_id: 项目ID
        db: 数据库会话

    Returns:
        分镜图片列表
    """
    try:
        # 验证项目是否存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        images = db.query(StoryboardImageModel).filter(
            StoryboardImageModel.project_id == project_id
        ).order_by(StoryboardImageModel.created_at.desc()).all()

        return images

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分镜图片列表失败: {str(e)}")


@router.delete("/{image_id}")
async def delete_storyboard_image(image_id: str, db: Session = Depends(get_db)):
    """
    删除分镜图片

    Args:
        image_id: 图片ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        image = db.query(StoryboardImageModel).filter(StoryboardImageModel.id == image_id).first()

        if not image:
            raise HTTPException(status_code=404, detail="分镜图片不存在")

        db.delete(image)
        db.commit()

        return {"message": "删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除分镜图片失败: {str(e)}")
