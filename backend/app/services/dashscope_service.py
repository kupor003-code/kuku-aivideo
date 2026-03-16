"""
阿里云 DashScope 服务

支持：
- 文生图（WanXiang）
- 图生图
- 视频生成
"""

import os
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from app.core.config import settings


class DashScopeService:
    """阿里云 DashScope 服务"""

    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.region = settings.DASHSCOPE_REGION
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"

    async def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        async_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        发起 HTTP 请求

        Args:
            endpoint: API 端点
            method: HTTP 方法
            data: 请求体数据
            params: URL 参数
            async_mode: 是否启用异步模式

        Returns:
            响应数据
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 如果是异步模式，添加异步header
        if async_mode:
            headers["X-DashScope-Async"] = "enable"

        async with httpx.AsyncClient(timeout=60.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            else:
                response = await client.post(url, headers=headers, json=data)

            response.raise_for_status()
            return response.json()

    async def text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1024*1024",
        n: int = 1,
        style: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        文生图（使用阿里云通义万相）- 异步调用

        Args:
            prompt: 提示词
            negative_prompt: 负面提示词
            size: 图片尺寸 (512*512, 768*768, 1024*1024, etc.)
            n: 生成数量
            style: 风格 (photography, anime, 3d, painting, etc.)

        Returns:
            生成结果
        """
        # API 端点 - 使用异步调用
        endpoint = "services/aigc/text2image/image-synthesis"

        # 构建请求参数
        request_data = {
            "model": "wanx-v1",
            "input": {
                "prompt": prompt,
            },
            "parameters": {
                "size": size,
                "n": n,
            }
        }

        # 添加可选参数
        if negative_prompt:
            request_data["input"]["negative_prompt"] = negative_prompt

        if style:
            request_data["parameters"]["style"] = style

        try:
            # 提交异步任务（启用async_mode）
            print(f"[DashScope] 提交文生图任务: {prompt[:50]}...")
            result = await self._make_request(endpoint, "POST", request_data, async_mode=True)
            print(f"[DashScope] 任务提交响应: {result}")

            # 检查是否有任务ID
            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                print(f"[DashScope] 任务ID: {task_id}")

                # 轮询查询任务结果（最多等待60秒）
                max_attempts = 30
                for attempt in range(max_attempts):
                    await self._wait_async_task_result(task_id)

                    # 获取任务结果
                    task_result = await self.get_async_task_result(task_id)
                    task_status = task_result.get("output", {}).get("task_status")
                    print(f"[DashScope] 轮询 {attempt+1}/{max_attempts}: 状态={task_status}")

                    if task_status == "SUCCEEDED":
                        # 任务成功，提取图片
                        results = task_result.get("output", {}).get("results", [])
                        print(f"[DashScope] 任务成功，生成 {len(results)} 张图片")
                        images = [
                            {
                                "url": img.get("url"),
                                "id": img.get("id"),
                            }
                            for img in results
                        ]
                        return {
                            "success": True,
                            "images": images,
                            "usage": task_result.get("usage", {}),
                        }
                    elif task_status == "FAILED":
                        error_msg = task_result.get("output", {}).get("message", "任务失败")
                        print(f"[DashScope] 任务失败: {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                        }

                    # 等待2秒后重试
                    await asyncio.sleep(2)

                print(f"[DashScope] 任务超时（已尝试 {max_attempts} 次）")
                return {
                    "success": False,
                    "error": "任务超时",
                }
            else:
                print(f"[DashScope] 未找到任务ID，响应: {result}")
                return {
                    "success": False,
                    "error": "未找到任务ID",
                    "raw_response": result,
                }

        except Exception as e:
            print(f"[DashScope] 异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
            }

    async def _wait_async_task_result(self, task_id: str, wait_time: float = 2.0):
        """等待异步任务完成"""
        import asyncio
        await asyncio.sleep(wait_time)

    async def get_async_task_result(self, task_id: str) -> Dict[str, Any]:
        """查询异步任务结果"""
        endpoint = f"tasks/{task_id}"
        return await self._make_request(endpoint, "GET")

    async def image_to_video(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        duration: float = 3.0,
        fps: int = 25,
    ) -> Dict[str, Any]:
        """
        图生视频（使用阿里云视频生成 API）

        Args:
            image_url: 输入图片 URL
            prompt: 提示词
            duration: 视频时长（秒）
            fps: 帧率

        Returns:
            生成结果
        """
        # API 端点（根据阿里云文档）
        endpoint = "services/aigc/video-generation/video-generation"

        # 构建请求参数
        request_data = {
            "model": "video-generation-v1",
            "input": {
                "image_url": image_url,
            },
            "parameters": {
                "duration": duration,
                "fps": fps,
            }
        }

        # 添加可选参数
        if prompt:
            request_data["input"]["prompt"] = prompt

        try:
            result = await self._make_request(endpoint, "POST", request_data)

            # 提取视频 URL
            if "output" in result and "video_url" in result["output"]:
                return {
                    "success": True,
                    "video_url": result["output"]["video_url"],
                    "video_id": result["output"].get("video_id"),
                    "duration": result["output"].get("duration", duration),
                    "usage": result.get("usage", {}),
                }
            else:
                return {
                    "success": False,
                    "error": "未找到生成的视频",
                    "raw_response": result,
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def text_to_video(
        self,
        prompt: str,
        duration: float = 3.0,
        fps: int = 25,
        resolution: str = "720p",
    ) -> Dict[str, Any]:
        """
        文生视频（使用阿里云视频生成 API）

        Args:
            prompt: 提示词
            duration: 视频时长（秒）
            fps: 帧率
            resolution: 分辨率 (480p, 720p, 1080p)

        Returns:
            生成结果
        """
        # API 端点
        endpoint = "services/aigc/text2video/video-generation"

        # 构建请求参数
        request_data = {
            "model": "video-generation-v1",
            "input": {
                "prompt": prompt,
            },
            "parameters": {
                "duration": duration,
                "fps": fps,
                "resolution": resolution,
            }
        }

        try:
            result = await self._make_request(endpoint, "POST", request_data)

            # 提取视频 URL
            if "output" in result and "video_url" in result["output"]:
                return {
                    "success": True,
                    "video_url": result["output"]["video_url"],
                    "video_id": result["output"].get("video_id"),
                    "duration": result["output"].get("duration", duration),
                    "usage": result.get("usage", {}),
                }
            else:
                return {
                    "success": False,
                    "error": "未找到生成的视频",
                    "raw_response": result,
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


# 全局实例
_dashscope_service: Optional[DashScopeService] = None


def get_dashscope_service() -> DashScopeService:
    """获取 DashScope 服务实例"""
    global _dashscope_service
    if _dashscope_service is None:
        _dashscope_service = DashScopeService()
    return _dashscope_service
