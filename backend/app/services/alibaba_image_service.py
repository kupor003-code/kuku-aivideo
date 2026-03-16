"""阿里云图片生成服务"""
from typing import List, Dict, Optional
import requests
import time
from app.core.config import settings


class AlibabaImageService:
    """阿里云通义万相图片生成服务"""

    def __init__(self):
        """初始化服务"""
        self.api_key = settings.DASHSCOPE_API_KEY
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY未配置")

        self.base_url = "https://dashscope.aliyuncs.com/api/v1"

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024*1024",
        n: int = 1,
        seed: Optional[int] = None,
    ) -> Dict:
        """
        文生图 - 异步生成图片

        Args:
            prompt: 提示词
            size: 图片尺寸 ("1024*1024", "720*1280", "1280*720")
            n: 生成数量
            seed: 随机种子（可选）

        Returns:
            包含task_id的响应
        """
        url = f"{self.base_url}/services/aigc/text2image/image-synthesis"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }

        data = {
            "model": "wanx-v1",
            "input": {"prompt": prompt},
            "parameters": {"size": size, "n": n},
        }

        if seed is not None:
            data["parameters"]["seed"] = seed

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()

            if "output" in result:
                return result["output"]
            else:
                raise Exception(f"API响应格式异常: {result}")

        except requests.exceptions.HTTPError as e:
            error_msg = response.json().get("message", str(e)) if response.content else str(e)
            raise Exception(f"文生图请求失败: {error_msg}")

    async def query_task(self, task_id: str) -> Dict:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态和结果
        """
        url = f"{self.base_url}/tasks/{task_id}"

        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = response.json().get("message", str(e)) if response.content else str(e)
            raise Exception(f"查询任务失败: {error_msg}")

    async def wait_for_completion(
        self,
        task_id: str,
        interval: int = 5,
        timeout: int = 300,
        callback=None,
    ) -> Dict:
        """
        等待任务完成

        Args:
            task_id: 任务ID
            interval: 轮询间隔（秒）
            timeout: 超时时间（秒）
            callback: 回调函数

        Returns:
            完整的任务结果
        """
        start_time = time.time()

        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                raise Exception(f"任务超时（{timeout}秒），task_id: {task_id}")

            # 查询任务状态
            result = await self.query_task(task_id)

            if "output" in result:
                task_status = result["output"].get("task_status", "UNKNOWN")

                # 调用回调函数
                if callback:
                    callback(task_status, result)

                # 检查任务状态
                if task_status == "SUCCEEDED":
                    return result
                elif task_status == "FAILED":
                    error_code = result["output"].get("code", "UNKNOWN")
                    error_msg = result["output"].get("message", "任务失败")
                    raise Exception(f"任务失败 [{error_code}]: {error_msg}")
                elif task_status in ["PENDING", "RUNNING"]:
                    time.sleep(interval)
                elif task_status == "UNKNOWN":
                    raise Exception(f"任务不存在或已过期（24小时），task_id: {task_id}")
                else:
                    raise Exception(f"未知任务状态: {task_status}")
            else:
                raise Exception(f"API响应格式异常: {result}")

    def get_image_url(self, task_result: Dict) -> List[str]:
        """
        从任务结果中提取图片URL

        Args:
            task_result: 任务结果

        Returns:
            图片URL列表
        """
        if "output" in task_result and "results" in task_result["output"]:
            return [item["url"] for item in task_result["output"]["results"]]
        return []


# 全局服务实例
_image_service: Optional[AlibabaImageService] = None


def get_alibaba_image_service() -> AlibabaImageService:
    """获取阿里云图片服务实例"""
    global _image_service
    if _image_service is None:
        _image_service = AlibabaImageService()
    return _image_service
