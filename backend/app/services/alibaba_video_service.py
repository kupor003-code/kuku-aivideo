"""阿里云视频生成服务"""
from typing import List, Dict, Optional
import requests
import time
import asyncio
from app.core.config import settings


class AlibabaVideoService:
    """阿里云通义万相视频生成服务"""

    def __init__(self):
        """初始化服务"""
        self.api_key = settings.DASHSCOPE_API_KEY
        # 即使没有API Key也允许使用模拟模式
        # if not self.api_key or self.api_key == "your-dashscope-api-key":
        #     raise ValueError("DASHSCOPE_API_KEY未配置")

        self.base_url = "https://dashscope.aliyuncs.com/api/v1"

    async def generate_video(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        duration: int = 5,
        fps: int = 30,
    ) -> Dict:
        """
        文生视频或图生视频 - 异步生成视频

        Args:
            prompt: 提示词
            image_url: 起始图片URL（可选，用于图生视频）
            duration: 视频时长（秒）
            fps: 帧率

        Returns:
            包含task_id的响应
        """
        # 注意：阿里云DashScope目前视频生成API可能尚未完全开放
        # 这里使用模拟服务返回成功响应
        # 如果API开放，只需将下面的mock代码替换为真实API调用

        import time
        import random

        # 模拟网络延迟
        await asyncio.sleep(2)

        # 返回模拟的任务ID
        task_id = f"video_task_{int(time.time())}_{random.randint(1000, 9999)}"

        return {
            "task_id": task_id,
            "status": "PENDING",
            "message": "✨ 模拟模式：视频生成功能（DashScope视频API可能尚未完全开放，当前使用模拟响应）"
        }

    async def query_task(self, task_id: str) -> Dict:
        """
        查询任务状态（模拟）

        Args:
            task_id: 任务ID

        Returns:
            任务状态和结果
        """
        # 模拟查询任务状态
        await asyncio.sleep(1)

        # 使用真实的示例视频URL（用于测试预览和下载功能）
        # 这里使用一些公开的示例视频
        sample_videos = [
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        ]

        # 根据task_id选择一个示例视频（保证同一个task_id总是返回同一个视频）
        import hashlib
        hash_value = int(hashlib.md5(task_id.encode()).hexdigest(), 16)
        video_url = sample_videos[hash_value % len(sample_videos)]

        return {
            "output": {
                "task_status": "SUCCEEDED",
                "results": [
                    {
                        "id": task_id,
                        "url": video_url,
                    }
                ]
            }
        }

    async def wait_for_completion(
        self,
        task_id: str,
        interval: int = 2,
        timeout: int = 120,  # 模拟模式下超时时间更短
        callback=None,
    ) -> Dict:
        """
        等待任务完成（模拟）

        Args:
            task_id: 任务ID
            interval: 轮询间隔（秒）
            timeout: 超时时间（秒）
            callback: 回调函数

        Returns:
            完整的任务结果
        """
        # 模拟进度更新
        for progress in [20, 40, 60, 80, 100]:
            if callback:
                callback(progress, None)
            await asyncio.sleep(0.5)

        return await self.query_task(task_id)

    def get_video_result(self, task_result: Dict) -> List[Dict]:
        """
        从任务结果中提取视频结果（包含id和url）

        Args:
            task_result: 任务结果

        Returns:
            视频结果列表，每个结果包含id和url
        """
        if "output" in task_result and "results" in task_result["output"]:
            return [
                {
                    "id": item.get("id", f"video_{i}"),
                    "url": item["url"]
                }
                for i, item in enumerate(task_result["output"]["results"])
            ]
        return []

    def get_video_url(self, task_result: Dict) -> List[str]:
        """
        从任务结果中提取视频URL（保持向后兼容）

        Args:
            task_result: 任务结果

        Returns:
            视频URL列表
        """
        results = self.get_video_result(task_result)
        return [item["url"] for item in results]


# 全局服务实例
_video_service: Optional[AlibabaVideoService] = None


def get_alibaba_video_service() -> AlibabaVideoService:
    """获取阿里云视频服务实例"""
    global _video_service
    if _video_service is None:
        _video_service = AlibabaVideoService()
    return _video_service
