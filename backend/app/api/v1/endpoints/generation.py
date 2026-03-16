"""
图片和视频生成 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.db.database import get_db
from app.services.dashscope_service import get_dashscope_service
from app.services.volcengine_service import get_volcengine_service
from pydantic import BaseModel
import uuid
import httpx
from urllib.parse import urlparse

router = APIRouter()


class ImageGenerationRequest(BaseModel):
    """图片生成请求"""
    prompt: str
    negative_prompt: Optional[str] = None
    size: str = "1024*1024"
    n: int = 1
    style: Optional[str] = None


class VideoGenerationRequest(BaseModel):
    """视频生成请求"""
    prompt: str
    image_url: Optional[str] = None  # 如果提供，则图生视频；否则文生视频
    duration: float = 3.0
    fps: int = 25
    resolution: str = "720p"
    enable_audio: bool = False  # 是否生成声音（使用Doubao-Seedance-1.5-pro）


@router.post("/generate/image")
async def generate_image(
    request: ImageGenerationRequest,
    db: Session = Depends(get_db),
):
    """
    生成图片（文生图）

    Args:
        request: 图片生成请求

    Returns:
        生成的图片 URL
    """
    try:
        print(f"[Generation] 收到图片生成请求: {request.prompt[:50]}...")
        dashscope_service = get_dashscope_service()

        # 调用阿里云通义万相 API
        result = await dashscope_service.text_to_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            size=request.size,
            n=request.n,
            style=request.style,
        )

        print(f"[Generation] 生成结果: success={result.get('success')}, error={result.get('error')}")

        if result.get("success"):
            return {
                "success": True,
                "images": result.get("images", []),
                "usage": result.get("usage", {}),
                "model": "wanx-v1",
                "model_name": "通义万相 (Wanxiang v1)",
            }
        else:
            print(f"[Generation] 图片生成失败: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"图片生成失败: {result.get('error', '未知错误')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Generation] 异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"图片生成失败: {str(e)}"
        )


@router.post("/generate/video")
async def generate_video(
    request: VideoGenerationRequest,
    db: Session = Depends(get_db),
):
    """
    生成视频（图生视频，使用豆包VolcEngine）

    Args:
        request: 视频生成请求

    Returns:
        生成的视频 URL
    """
    try:
        print(f"[Generation] 收到视频生成请求: image_url={request.image_url[:50] if request.image_url else None}..., duration={request.duration}")
        volcengine_service = get_volcengine_service()

        # 使用豆包图生视频API
        if request.image_url:
            result = await volcengine_service.image_to_video(
                image_url=request.image_url,
                prompt=request.prompt,
                duration=request.duration,
                enable_audio=request.enable_audio,
            )
        else:
            # 如果没有图片URL，返回错误
            print(f"[Generation] 错误: 缺少图片URL")
            raise HTTPException(
                status_code=400,
                detail="视频生成需要提供图片URL（图生视频）"
            )

        print(f"[Generation] 生成结果: success={result.get('success')}, error={result.get('error')}")

        if result.get("success"):
            return {
                "success": True,
                "video_url": result.get("video_url"),
                "video_id": result.get("video_id"),
                "duration": result.get("duration"),
                "usage": result.get("usage", {}),
                "model": "doubao-seedance-1-5-pro-251215",
                "model_name": "豆包视频生成 (Seedance 1.5 Pro)",
            }
        else:
            print(f"[Generation] 视频生成失败: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"视频生成失败: {result.get('error', '未知错误')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Generation] 异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"视频生成失败: {str(e)}"
        )


@router.get("/models")
async def list_models():
    """
    列出可用的生成模型

    Returns:
        模型列表
    """
    return {
        "image_models": [
            {
                "id": "wanx-v1",
                "name": "通义万相",
                "type": "text2image",
                "description": "阿里云通义万相AI文生图模型",
                "supported_sizes": ["1024*1024", "720*1280", "1280*720"],
            }
        ],
        "video_models": [
            {
                "id": "doubao-seedance-1-5-pro-251215",
                "name": "豆包视频生成",
                "type": "image2video",
                "description": "火山引擎豆包AI视频生成模型 (Seedance 1.5 Pro)",
                "supported_durations": [2, 3, 4, 5],
                "supports_audio": True,  # 支持音频生成
            }
        ]
    }


@router.get("/proxy/download")
async def proxy_download(url: str):
    """
    代理下载图片/视频（解决CORS问题）

    Args:
        url: 要下载的资源URL

    Returns:
        文件流
    """
    try:
        # 验证URL格式
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL")

        # 从URL推断文件类型
        url_lower = url.lower()
        if url_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            media_type = 'image/jpeg'
        elif url_lower.endswith(('.mp4', '.mov', '.avi', '.webm')):
            media_type = 'video/mp4'
        else:
            # 根据URL路径判断
            if '/image' in url_lower or 'jpg' in url_lower or 'png' in url_lower:
                media_type = 'image/jpeg'
            elif '/video' in url_lower or 'mp4' in url_lower:
                media_type = 'video/mp4'
            else:
                media_type = 'application/octet-stream'

        # 使用代理下载
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            # 返回文件流
            return StreamingResponse(
                response.aiter_bytes(),
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{parsed_url.path.split("/")[-1] or "download"}"',
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET",
                    "Access-Control-Allow-Headers": "*",
                }
            )

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
