"""V2 Agent基类"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class AgentMessage:
    """Agent消息系统"""
    def __init__(
        self,
        sender: str,
        receiver: str,
        content: str,
        message_type: str = "request",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.sender = sender  # 发送者agent类型
        self.receiver = receiver  # 接收者agent类型
        self.content = content
        self.message_type = message_type  # request, response, notification
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()


class AgentResponse:
    """Agent响应"""
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        message: str = "",
        error: Optional[str] = None,
        next_agent: Optional[str] = None,
    ):
        self.success = success
        self.data = data or {}
        self.message = message
        self.error = error
        self.next_agent = next_agent  # 下一个应该执行的agent


class BaseAgentV2(ABC):
    """V2 Agent基类"""

    def __init__(self):
        self.agent_type: str = "base"
        self.agent_name: str = "基础Agent"
        self.description: str = ""
        self.capabilities: List[str] = []

    @abstractmethod
    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        处理任务的主方法

        Args:
            input_data: 输入数据
            context: 上下文信息

        Returns:
            AgentResponse: 处理结果
        """
        pass

    @abstractmethod
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据

        Args:
            input_data: 输入数据

        Returns:
            bool: 是否有效
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "agent_type": self.agent_type,
            "agent_name": self.agent_name,
            "description": self.description,
            "capabilities": self.capabilities,
        }

    async def send_message(
        self,
        receiver: str,
        content: str,
        message_type: str = "request",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        """
        发送消息给其他Agent

        Args:
            receiver: 接收者agent类型
            content: 消息内容
            message_type: 消息类型
            metadata: 元数据

        Returns:
            AgentMessage: 创建的消息
        """
        return AgentMessage(
            sender=self.agent_type,
            receiver=receiver,
            content=content,
            message_type=message_type,
            metadata=metadata,
        )

    async def receive_message(self, message: AgentMessage) -> AgentResponse:
        """
        接收并处理来自其他Agent的消息

        Args:
            message: 接收到的消息

        Returns:
            AgentResponse: 处理结果
        """
        # 默认实现：直接处理消息内容
        return await self.process(
            {"message": message.content, "metadata": message.metadata},
            context={"sender": message.sender},
        )
