"""智谱AI服务"""
from typing import List, Dict, Optional
from zhipuai import ZhipuAI
from app.core.config import settings


class ZhipuAIService:
    """智谱AI服务"""

    def __init__(self):
        """初始化服务"""
        if not settings.ZHIPUAI_API_KEY:
            raise ValueError("ZHIPUAI_API_KEY未配置")

        self.client = ZhipuAI(api_key=settings.ZHIPUAI_API_KEY)
        self.model = "glm-4-flash"  # 使用Flash模型，速度快

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> str:
        """
        对话接口

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            AI回复
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"智谱AI调用失败: {str(e)}")

    async def chat_with_system_prompt(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        使用系统提示词的对话

        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            context: 上下文信息
            temperature: 温度参数

        Returns:
            AI回复
        """
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # 如果有上下文，添加到用户消息中
        if context:
            user_message = f"对话历史：\n{context}\n\n当前问题：{user_message}"

        messages.append({"role": "user", "content": user_message})

        return await self.chat(messages, temperature=temperature)


# 全局服务实例
_zhipuai_service: Optional[ZhipuAIService] = None


def get_zhipuai_service() -> ZhipuAIService:
    """获取智谱AI服务实例"""
    global _zhipuai_service
    if _zhipuai_service is None:
        _zhipuai_service = ZhipuAIService()
    return _zhipuai_service
