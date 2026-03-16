"""模拟图片生成服务 - 用于演示"""
from typing import List, Dict, Optional
import time
import random


class MockImageService:
    """模拟图片生成服务"""

    def __init__(self):
        """初始化服务"""
        # 示例图片URL（使用公开的示例图片）
        self.sample_images = [
            "https://picsum.photos/1024/1024?random=1",
            "https://picsum.photos/1024/1024?random=2",
            "https://picsum.photos/1024/1024?random=3",
            "https://picsum.photos/1024/1024?random=4",
        ]

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024*1024",
        n: int = 1,
        seed: Optional[int] = None,
    ) -> Dict:
        """
        模拟文生图 - 返回示例图片

        Args:
            prompt: 提示词
            size: 图片尺寸
            n: 生成数量
            seed: 随机种子

        Returns:
            包含task_id的响应
        """
        # 模拟网络延迟
        await asyncio.sleep(1)

        task_id = f"mock_task_{int(time.time())}_{random.randint(1000, 9999)}"

        return {
            "task_id": task_id,
            "status": "PENDING",
            "message": "✨ 模拟模式：使用示例图片（需配置DashScope API Key生成真实图片）"
        }

    async def query_task(self, task_id: str) -> Dict:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态和结果
        """
        # 模拟任务已完成
        return {
            "output": {
                "task_status": "SUCCEEDED",
                "results": [
                    {
                        "url": f"https://picsum.photos/1024/1024?random={random.randint(1, 1000)}",
                        "prompt": "示例图片"
                    }
                    for _ in range(2)  # 默认返回2张
                ]
            }
        }

    async def wait_for_completion(
        self,
        task_id: str,
        interval: int = 2,
        timeout: int = 60,
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
        # 模拟处理时间
        for progress in [20, 40, 60, 80, 100]:
            if callback:
                callback(progress)
            await asyncio.sleep(0.5)

        return await self.query_task(task_id)

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
_image_service = None


def get_mock_image_service() -> MockImageService:
    """获取模拟图片服务实例"""
    global _image_service
    if _image_service is None:
        _image_service = MockImageService()
    return _image_service


# 添加asyncio导入
import asyncio
