"""文件存储服务 - 管理项目文件夹和内容保存"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote
from app.core.config import settings


class FileStorageService:
    """文件存储服务"""

    def __init__(self):
        self.projects_dir = Path(settings.PROJECTS_DIR)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def get_project_dir(self, project_id: str) -> Path:
        """获取项目文件夹路径"""
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def get_images_dir(self, project_id: str) -> Path:
        """获取项目图片文件夹"""
        images_dir = self.get_project_dir(project_id) / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        return images_dir

    def get_videos_dir(self, project_id: str) -> Path:
        """获取项目视频文件夹"""
        videos_dir = self.get_project_dir(project_id) / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)
        return videos_dir

    def save_image(
        self,
        project_id: str,
        image_url: str,
        image_id: str,
        image_data: bytes
    ) -> Dict[str, str]:
        """
        保存图片到本地
        
        Args:
            project_id: 项目ID
            image_url: 原始图片URL
            image_id: 图片ID
            image_data: 图片二进制数据
            
        Returns:
            {
                "local_path": "projects/xxx/images/image_1.png",
                "file_url": "/api/v1/files/projects/xxx/images/image_1.png"
            }
        """
        try:
            images_dir = self.get_images_dir(project_id)
            
            # 确定文件扩展名
            ext = self._get_extension_from_url(image_url) or ".png"
            filename = f"image_{image_id}{ext}"
            file_path = images_dir / filename
            
            # 保存文件
            file_path.write_bytes(image_data)
            
            # 返回相对路径和访问URL
            relative_path = f"projects/{project_id}/images/{filename}"
            file_url = f"/api/v1/files/{quote(relative_path)}"
            
            return {
                "local_path": str(relative_path),
                "file_url": file_url
            }
        except Exception as e:
            raise Exception(f"保存图片失败: {str(e)}")

    def save_video(
        self,
        project_id: str,
        video_url: str,
        video_id: str,
        video_data: bytes
    ) -> Dict[str, str]:
        """
        保存视频到本地
        
        Args:
            project_id: 项目ID
            video_url: 原始视频URL
            video_id: 视频ID
            video_data: 视频二进制数据
            
        Returns:
            {
                "local_path": "projects/xxx/videos/video_1.mp4",
                "file_url": "/api/v1/files/projects/xxx/videos/video_1.mp4"
            }
        """
        try:
            videos_dir = self.get_videos_dir(project_id)
            
            # 确定文件扩展名
            ext = self._get_extension_from_url(video_url) or ".mp4"
            filename = f"video_{video_id}{ext}"
            file_path = videos_dir / filename
            
            # 保存文件
            file_path.write_bytes(video_data)
            
            # 返回相对路径和访问URL
            relative_path = f"projects/{project_id}/videos/{filename}"
            file_url = f"/api/v1/files/{quote(relative_path)}"
            
            return {
                "local_path": str(relative_path),
                "file_url": file_url
            }
        except Exception as e:
            raise Exception(f"保存视频失败: {str(e)}")

    def get_project_images(self, project_id: str) -> List[Dict[str, str]]:
        """获取项目所有图片"""
        images_dir = self.get_images_dir(project_id)
        images = []
        
        if images_dir.exists():
            for file_path in sorted(images_dir.glob("*")):
                if file_path.is_file() and file_path.suffix in [".png", ".jpg", ".jpeg", ".webp"]:
                    relative_path = f"projects/{project_id}/images/{file_path.name}"
                    file_url = f"/api/v1/files/{quote(relative_path)}"
                    images.append({
                        "filename": file_path.name,
                        "local_path": str(relative_path),
                        "file_url": file_url,
                        "size": file_path.stat().st_size
                    })
        
        return images

    def get_project_videos(self, project_id: str) -> List[Dict[str, str]]:
        """获取项目所有视频"""
        videos_dir = self.get_videos_dir(project_id)
        videos = []
        
        if videos_dir.exists():
            for file_path in sorted(videos_dir.glob("*")):
                if file_path.is_file() and file_path.suffix in [".mp4", ".webm", ".avi", ".mov"]:
                    relative_path = f"projects/{project_id}/videos/{file_path.name}"
                    file_url = f"/api/v1/files/{quote(relative_path)}"
                    videos.append({
                        "filename": file_path.name,
                        "local_path": str(relative_path),
                        "file_url": file_url,
                        "size": file_path.stat().st_size
                    })
        
        return videos

    def delete_project(self, project_id: str) -> bool:
        """删除项目文件夹及所有内容"""
        try:
            project_dir = self.get_project_dir(project_id)
            if project_dir.exists():
                shutil.rmtree(project_dir)
            return True
        except Exception as e:
            print(f"删除项目文件夹失败: {str(e)}")
            return False

    def get_file(self, relative_path: str) -> Optional[bytes]:
        """获取文件内容"""
        try:
            file_path = self.projects_dir / relative_path
            if file_path.exists() and file_path.is_file():
                return file_path.read_bytes()
            return None
        except Exception as e:
            print(f"获取文件失败: {str(e)}")
            return None

    @staticmethod
    def _get_extension_from_url(url: str) -> Optional[str]:
        """从URL提取文件扩展名"""
        try:
            # 移除查询参数
            path = url.split("?")[0]
            # 获取最后一个点之后的内容
            if "." in path:
                ext = path.split(".")[-1].lower()
                if ext in ["png", "jpg", "jpeg", "webp", "gif", "mp4", "webm", "avi", "mov"]:
                    return f".{ext}"
        except Exception:
            pass
        return None


# 全局实例
file_storage_service = FileStorageService()
