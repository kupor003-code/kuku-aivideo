"""Agent基类"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self):
        self.agent_type: str = ""
        self.name: str = ""
        self.description: str = ""

    @abstractmethod
    async def chat(self, message: str, context: Dict) -> str:
        """
        处理对话消息

        Args:
            message: 用户消息
            context: 对话上下文

        Returns:
            Agent回复
        """
        pass

    @abstractmethod
    async def suggest(self, context: Dict) -> List[str]:
        """
        基于上下文提供建议

        Args:
            context: 对话上下文

        Returns:
            建议列表
        """
        pass

    def _build_context_str(self, context: Dict) -> str:
        """构建上下文字符串"""
        messages = context.get("messages", [])
        if not messages:
            return ""

        context_parts = []
        for msg in messages[-5:]:  # 只取最近5条消息
            role = msg.get("role", "user")
            content = msg.get("content", "")
            role_name = {"user": "用户", "assistant": "AI"}.get(role, role)
            context_parts.append(f"{role_name}: {content}")

        return "\n".join(context_parts)
