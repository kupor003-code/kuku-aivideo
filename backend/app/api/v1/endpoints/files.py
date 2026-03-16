"""文件服务 API - 处理项目文件的获取和访问"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
from urllib.parse import unquote
import mimetypes

from app.db.database import get_db
from app.services.file_storage_service import file_storage_service
from app.models.project import Project
from app.models.storyboard import StoryboardImage
from app.models.video_generation import VideoGeneration

router = APIRouter()


@router.get("/files/{file_path:path}")
async def get_file(file_path: str):
    """
    获取项目文件
    
    Path: /api/v1/files/projects/{project_id}/images/{filename}
          /api/v1/files/projects/{project_id}/videos/{filename}
    """
    try:
        # 解码路径
        file_path = unquote(file_path)
        
        # 获取文件内容
        file_content = file_storage_service.get_file(file_path)
        if not file_content:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 确定 MIME 类型
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        # 返回文件
        return StreamingResponse(
            iter([file_content]),
            media_type=mime_type,
            headers={"Content-Disposition": f"inline; filename={Path(file_path).name}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件失败: {str(e)}")


@router.get("/projects/{project_id}/images")
async def get_project_images(project_id: str, db: Session = Depends(get_db)):
    """获取项目所有图片"""
    try:
        # 验证项目存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 从数据库获取图片
        images = db.query(StoryboardImage).filter(
            StoryboardImage.project_id == project_id
        ).order_by(StoryboardImage.created_at.desc()).all()
        
        result = []
        for image in images:
            result.append({
                "id": image.id,
                "url": image.local_url or image.url,  # 优先使用本地 URL
                "local_path": image.file_path,
                "prompt": image.meta.get("prompt", ""),
                "size": image.meta.get("size", ""),
                "created_at": image.created_at.isoformat()
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图片列表失败: {str(e)}")


@router.get("/projects/{project_id}/videos")
async def get_project_videos(project_id: str, db: Session = Depends(get_db)):
    """获取项目所有视频"""
    try:
        # 验证项目存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 从数据库获取视频
        videos = db.query(VideoGeneration).filter(
            VideoGeneration.project_id == project_id
        ).order_by(VideoGeneration.created_at.desc()).all()
        
        result = []
        for video in videos:
            result.append({
                "id": video.id,
                "url": video.video_local_url or video.video_url,  # 优先使用本地 URL
                "local_path": video.video_file_path,
                "thumbnail": video.thumbnail_url,
                "status": video.status.value if video.status else "pending",
                "duration": video.generation_params.get("duration", 0),
                "fps": video.generation_params.get("fps", 30),
                "created_at": video.created_at.isoformat()
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取视频列表失败: {str(e)}")


@router.get("/projects/{project_id}/content")
async def get_project_content(project_id: str, db: Session = Depends(get_db)):
    """
    获取项目的完整内容（图片和视频）
    用于项目打开时一次性加载所有内容
    """
    try:
        # 验证项目存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 获取所有图片
        images = db.query(StoryboardImage).filter(
            StoryboardImage.project_id == project_id
        ).order_by(StoryboardImage.created_at.asc()).all()
        
        images_data = []
        for image in images:
            images_data.append({
                "id": image.id,
                "url": image.local_url or image.url,
                "prompt": image.meta.get("prompt", ""),
                "size": image.meta.get("size", ""),
                "created_at": image.created_at.isoformat()
            })
        
        # 获取所有视频
        videos = db.query(VideoGeneration).filter(
            VideoGeneration.project_id == project_id
        ).order_by(VideoGeneration.created_at.asc()).all()
        
        videos_data = []
        for video in videos:
            videos_data.append({
                "id": video.id,
                "url": video.video_local_url or video.video_url,
                "thumbnail": video.thumbnail_url,
                "status": video.status.value if video.status else "pending",
                "duration": video.generation_params.get("duration", 0),
                "created_at": video.created_at.isoformat()
            })
        
        return {
            "project_id": project_id,
            "images": images_data,
            "videos": videos_data,
            "total_images": len(images_data),
            "total_videos": len(videos_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目内容失败: {str(e)}")
