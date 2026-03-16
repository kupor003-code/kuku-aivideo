"""Agent管理器"""
from typing import Dict, Optional
from app.agents.creative_agent import CreativeAgent
from app.agents.storyboard_agent import StoryboardAgent
from app.agents.video_agent import VideoAgent
from app.agents.coordinator_agent import CoordinatorAgent


class AgentManager:
    """Agent管理器 - 管理所有Agent实例"""

    def __init__(self):
        """初始化Agent管理器"""
        self._agents: Dict[str, object] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        """注册默认Agent"""
        self.register("creative", CreativeAgent())
        self.register("storyboard", StoryboardAgent())
        self.register("video", VideoAgent())
        self.register("coordinator", CoordinatorAgent())
        # 其他Agent后续添加
        # self.register("director", DirectorAgent())
        # self.register("prompt", PromptAgent())

    def register(self, agent_type: str, agent: object):
        """
        注册Agent

        Args:
            agent_type: Agent类型
            agent: Agent实例
        """
        self._agents[agent_type] = agent

    def get(self, agent_type: str) -> Optional[object]:
        """
        获取Agent实例

        Args:
            agent_type: Agent类型

        Returns:
            Agent实例或None
        """
        return self._agents.get(agent_type)

    def get_creative_agent(self) -> CreativeAgent:
        """获取创意发散Agent"""
        agent = self.get("creative")
        if not agent:
            raise Exception("创意发散Agent未注册")
        return agent

    def get_storyboard_agent(self) -> StoryboardAgent:
        """获取分镜生成Agent"""
        agent = self.get("storyboard")
        if not agent:
            raise Exception("分镜生成Agent未注册")
        return agent

    def get_coordinator_agent(self) -> CoordinatorAgent:
        """获取协调Agent"""
        agent = self.get("coordinator")
        if not agent:
            raise Exception("协调Agent未注册")
        return agent

    def get_video_agent(self) -> VideoAgent:
        """获取视频生成Agent"""
        agent = self.get("video")
        if not agent:
            raise Exception("视频生成Agent未注册")
        return agent


# 全局Agent管理器实例
_agent_manager: Optional[AgentManager] = None


def get_agent_manager() -> AgentManager:
    """获取Agent管理器实例"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager
