"""V2 Agent系统 - AI导演团队"""
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse, AgentMessage
from app.agents.v2.orchestrator_agent import OrchestratorAgent
from app.agents.v2.director_agent import DirectorAgent
from app.agents.v2.producer_agent import ProducerAgent
from app.agents.v2.storyboard_agent import StoryboardAgent
from app.agents.v2.consistency_agent import ConsistencyAgent
from app.agents.v2.video_agent import VideoAgent
from app.agents.v2.agent_manager_v2 import AgentManagerV2, get_agent_manager_v2

__all__ = [
    "BaseAgentV2",
    "AgentResponse",
    "AgentMessage",
    "OrchestratorAgent",
    "DirectorAgent",
    "ProducerAgent",
    "StoryboardAgent",
    "ConsistencyAgent",
    "VideoAgent",
    "AgentManagerV2",
    "get_agent_manager_v2",
]
