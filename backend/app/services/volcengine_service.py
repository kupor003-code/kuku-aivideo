"""
豆包（VolcEngine）AI服务

支持：
- 文生图
- 图生视频
- 视频生成
"""

import os
import httpx
import asyncio
from typing import Dict, Any, Optional
from app.core.config import settings


class VolcEngineService:
    """豆包 AI 服务"""

    def __init__(self):
        self.api_key = settings.VOLCENGINE_API_KEY
        # 豆包API端点 - 使用方舟大模型服务
        self.image_base_url = "https://ark.cn-beijing.volces.com/api/v3"

    async def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        发起 HTTP 请求

        Args:
            endpoint: API 端点
            method: HTTP 方法
            data: 请求体数据
            params: URL 参数
            headers: 额外的请求头

        Returns:
            响应数据
        """
        url = f"{self.image_base_url}/{endpoint}"
        default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if headers:
            default_headers.update(headers)

        async with httpx.AsyncClient(timeout=120.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=default_headers, params=params)
            else:
                response = await client.post(url, headers=default_headers, json=data)

            response.raise_for_status()
            return response.json()

    async def text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "2K",
        n: int = 1,
        style: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        文生图（使用豆包AI - doubao-seedream-5-0-260128）

        Args:
            prompt: 提示词
            negative_prompt: 负面提示词
            size: 图片尺寸 (默认2K，支持2K/3K或具体像素值如2048x2048)
            n: 生成数量
            style: 风格

        Returns:
            生成结果
        """
        try:
            # 调用豆包文生图API
            # 使用正确的模型 ID（带日期后缀）
            endpoint = "images/generations"

            request_data = {
                "model": "doubao-seedream-5-0-260128",  # 正确的模型ID
                "prompt": prompt,
                "size": size,  # 支持 "2K", "3K" 或具体像素值
                "response_format": "url",  # 返回URL格式
                "watermark": False,  # 不添加水印
                "stream": False,  # 非流式输出
            }

            # 如果需要生成多张图片，使用sequential_image_generation
            if n > 1:
                request_data["sequential_image_generation"] = "auto"
                request_data["sequential_image_generation_options"] = {
                    "max_images": n
                }
            else:
                request_data["sequential_image_generation"] = "disabled"

            # 添加可选参数
            if negative_prompt:
                # Note: 豆包API可能不直接支持negative_prompt
                # 可以将其添加到prompt中
                request_data["prompt"] = f"{prompt}\n(避免: {negative_prompt})"

            if style:
                request_data["prompt"] = f"{request_data['prompt']}\n风格: {style}"

            # 提交请求
            result = await self._make_request(endpoint, "POST", request_data)

            # 检查响应是否有错误
            if "error" in result:
                return {
                    "success": False,
                    "error": result.get("error", {}).get("message", "API错误"),
                    "raw_response": result,
                }

            # 检查响应
            if "data" in result:
                # API 返回图片数据
                images = result.get("data", [])

                # 处理成功的图片
                successful_images = []
                for img in images:
                    if "error" not in img:
                        successful_images.append({
                            "url": img.get("url", ""),
                            "b64_json": img.get("b64_json"),
                            "size": img.get("size", size),
                        })

                if successful_images:
                    return {
                        "success": True,
                        "images": successful_images,
                        "model": result.get("model", ""),
                        "usage": result.get("usage", {}),
                    }
                else:
                    return {
                        "success": False,
                        "error": "所有图片生成失败",
                        "raw_response": result,
                    }
            else:
                return {
                    "success": False,
                    "error": "未找到图片数据",
                    "raw_response": result,
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def image_to_video(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        duration: float = 3.0,
        enable_audio: bool = False,  # 是否生成声音
    ) -> Dict[str, Any]:
        """
        图生视频（使用豆包视频生成API - doubao-seedance-1-5-pro-251215）

        Args:
            image_url: 输入图片 URL
            prompt: 提示词
            duration: 视频时长（秒）
            enable_audio: 是否生成声音（默认False）

        Returns:
            生成结果
        """
        try:
            print(f"[VolcEngine] 提交图生视频任务")
            print(f"[VolcEngine] 图片URL: {image_url[:100]}...")
            print(f"[VolcEngine] 时长: {duration}秒")

            # 调用豆包图生视频API
            # 使用正确的模型 ID
            endpoint = "contents/generations/tasks"  # ✅ 注意是 contents 不是 content

            # 构建文本提示词（不包含命令行参数）
            text_prompt = prompt or "根据图片生成视频"

            request_data = {
                "model": "doubao-seedance-1-5-pro-251215",  # 正确的模型ID
                "content": [
                    {
                        "type": "text",
                        "text": text_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url  # ✅ 正确的格式：image_url 是一个对象
                        }
                    }
                ]
            }

            print(f"[VolcEngine] 请求数据: {request_data}")

            # 提交异步任务
            result = await self._make_request(endpoint, "POST", request_data)
            print(f"[VolcEngine] 任务提交响应: {result}")

            if "id" in result:
                task_id = result["id"]
                print(f"[VolcEngine] 任务ID: {task_id}")

                # 轮询查询任务结果（最多等待120秒）
                max_attempts = 60
                for attempt in range(max_attempts):
                    await asyncio.sleep(2)

                    # 查询视频任务状态
                    status_result = await self.get_video_task_status(task_id)
                    task_status = status_result.get("status")
                    print(f"[VolcEngine] 轮询 {attempt+1}/{max_attempts}: 状态={task_status}")

                    if task_status == "succeeded":
                        # 任务成功
                        video_url = status_result.get("content", {}).get("video_url")
                        print(f"[VolcEngine] 视频生成成功: {video_url}")
                        return {
                            "success": True,
                            "video_url": video_url,
                            "video_id": task_id,
                            "duration": duration,
                            "task_id": task_id,
                        }
                    elif task_status in ["pending", "processing"]:
                        continue
                    elif task_status == "failed":
                        error_msg = status_result.get("error", "任务失败")
                        print(f"[VolcEngine] 任务失败: {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                        }

                print(f"[VolcEngine] 任务超时（已尝试 {max_attempts} 次）")
                return {
                    "success": False,
                    "error": "任务超时",
                }
            else:
                print(f"[VolcEngine] 未找到任务ID，响应: {result}")
                return {
                    "success": False,
                    "error": "未找到任务ID",
                    "raw_response": result,
                }

        except Exception as e:
            print(f"[VolcEngine] 异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
            }

    async def get_video_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询视频任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态
        """
        try:
            endpoint = f"contents/generations/tasks/{task_id}"

            result = await self._make_request(endpoint, "GET")
            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }


# 全局服务实例
_volcengine_service: Optional[VolcEngineService] = None


def get_volcengine_service() -> VolcEngineService:
    """获取豆包服务实例"""
    global _volcengine_service
    if _volcengine_service is None:
        _volcengine_service = VolcEngineService()
    return _volcengine_service
