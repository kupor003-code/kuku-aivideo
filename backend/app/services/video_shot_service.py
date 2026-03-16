"""Video Shot Agent服务 - 调用剧本分镜智能体"""
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)


class VideoShotService:
    """剧本分镜智能体服务客户端"""

    def __init__(self):
        """初始化服务"""
        self.base_url = "http://localhost:8001/api/v1"
        self.timeout = 300.0  # 5分钟超时

    async def generate_storyboard(
        self,
        script_text: str,
        task_id: Optional[str] = None,
        max_fragment_duration: int = 10,
        model_name: str = "glm-4-flash",
    ) -> Dict[str, Any]:
        """
        生成分镜脚本

        Args:
            script_text: 剧本文本
            task_id: 任务ID（可选）
            max_fragment_duration: 最大片段时长（秒）
            model_name: 使用的LLM模型

        Returns:
            分镜结果
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 准备请求数据
                payload = {
                    "script": script_text,
                    "config": {
                        "max_fragment_duration": max_fragment_duration,
                        "model_name": model_name,
                        "temperature": 0.7,
                    }
                }

                if task_id:
                    payload["task_id"] = task_id

                # 调用API
                response = await client.post(
                    f"{self.base_url}/storyboard",
                    json=payload,
                )

                response.raise_for_status()
                result = response.json()

                # 等待任务完成
                if result.get("status") == "pending":
                    task_id = result.get("task_id")
                    return await self._wait_for_completion(task_id)

                return result

        except httpx.HTTPError as e:
            logger.error(f"调用video-shot-agent失败: {str(e)}")
            raise Exception(f"剧本分镜服务调用失败: {str(e)}")
        except Exception as e:
            logger.error(f"生成剧本分镜失败: {str(e)}")
            raise

    async def _wait_for_completion(
        self,
        task_id: str,
        interval: float = 2.0,
        max_wait: float = 120.0,
    ) -> Dict[str, Any]:
        """
        等待任务完成

        Args:
            task_id: 任务ID
            interval: 轮询间隔（秒）
            max_wait: 最大等待时间（秒）

        Returns:
            任务结果
        """
        start_time = asyncio.get_event_loop().time()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                # 检查超时
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > max_wait:
                    raise TimeoutError(f"任务超时: {task_id}")

                # 查询任务状态
                response = await client.get(
                    f"{self.base_url}/storyboard/status/{task_id}"
                )
                response.raise_for_status()
                result = response.json()

                status = result.get("status")

                if status == "completed":
                    logger.info(f"任务完成: {task_id}")
                    return result
                elif status == "failed":
                    error_msg = result.get("error", "未知错误")
                    raise Exception(f"任务失败: {error_msg}")
                elif status in ["pending", "processing"]:
                    logger.debug(f"任务处理中: {task_id}, 进度: {result.get('progress', 0)}%")
                    await asyncio.sleep(interval)
                else:
                    raise Exception(f"未知状态: {status}")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/storyboard/status/{task_id}"
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            raise

    def convert_to_canvas_format(
        self,
        storyboard_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        将video-shot-agent的分镜结果转换为Canvas节点格式

        Args:
            storyboard_result: 分镜结果

        Returns:
            Canvas场景列表
        """
        scenes = []

        data = storyboard_result.get("data", {})
        shots = data.get("shots", [])

        # 按场景分组（如果有的话）
        current_scene = {
            "scene_number": 1,
            "description": "",
            "shots": [],
        }

        for i, shot in enumerate(shots):
            shot_data = {
                "shot_number": shot.get("shot_number", i + 1),
                "description": shot.get("scene_description", ""),
                "duration": shot.get("duration", 5),
                "camera_angle": shot.get("camera_angle", "中景"),
                "camera_movement": shot.get("camera_movement", "固定"),
                "chinese_prompt": shot.get("chinese_prompt", ""),
                "english_prompt": shot.get("english_prompt", ""),
                "audio_prompt": shot.get("audio_prompt", ""),
                # video-shot-agent特有字段
                "continuity": shot.get("continuity", {}),
                "characters": shot.get("characters", []),
                "location": shot.get("location", ""),
                "time_of_day": shot.get("time_of_day", ""),
            }

            current_scene["shots"].append(shot_data)

        current_scene["total_shots"] = len(current_scene["shots"])
        scenes.append(current_scene)

        return scenes


# 全局服务实例
_video_shot_service: Optional[VideoShotService] = None


def get_video_shot_service() -> VideoShotService:
    """获取video-shot-agent服务实例"""
    global _video_shot_service
    if _video_shot_service is None:
        _video_shot_service = VideoShotService()
    return _video_shot_service
