"""Agent Manager V2 - 管理多Agent协作"""
from typing import Dict, List, Any, Optional
from app.agents.v2.orchestrator_agent import OrchestratorAgent
from app.agents.v2.director_agent import DirectorAgent
from app.agents.v2.producer_agent import ProducerAgent
from app.agents.v2.storyboard_agent import StoryboardAgent
from app.agents.v2.consistency_agent import ConsistencyAgent
from app.agents.v2.video_agent import VideoAgent
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse, AgentMessage


class AgentManagerV2:
    """
    Agent Manager V2 - 管理AI导演团队的协作
    """

    def __init__(self):
        """初始化Agent Manager"""
        self.agents: Dict[str, BaseAgentV2] = {}
        self._register_agents()
        self.conversation_history: List[AgentMessage] = []

    def _register_agents(self):
        """注册所有Agent"""
        self.agents = {
            "orchestrator": OrchestratorAgent(),
            "director": DirectorAgent(),
            "producer": ProducerAgent(),
            "storyboard": StoryboardAgent(),
            "consistency": ConsistencyAgent(),
            "video": VideoAgent(),
        }

    def get_agent(self, agent_type: str) -> Optional[BaseAgentV2]:
        """
        获取指定Agent

        Args:
            agent_type: Agent类型

        Returns:
            Agent实例
        """
        return self.agents.get(agent_type)

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        列出所有Agent

        Returns:
            Agent信息列表
        """
        return [agent.get_info() for agent in self.agents.values()]

    async def execute_workflow(
        self,
        user_input: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        执行完整的创作工作流

        Args:
            user_input: 用户输入
            project_id: 项目ID

        Returns:
            执行结果
        """
        try:
            # 1. 由Orchestrator解析用户意图并生成执行计划
            orchestrator = self.get_agent("orchestrator")
            if not orchestrator:
                return {"success": False, "error": "Orchestrator Agent未找到"}

            # 第一步：解析用户输入
            response = await orchestrator.process(
                {"user_input": user_input},
                context={"project_id": project_id},
            )

            if not response.success:
                return {"success": False, "error": response.error}

            # 记录初始响应
            execution_plan = response.data.get("execution_plan")
            current_context = {
                "project_id": project_id,
                "user_input": user_input,
                "execution_plan": execution_plan,
            }

            results = {
                "orchestrator": response.data,
                "plan": execution_plan,
            }

            # 2. 按照执行计划依次执行每个Agent
            if execution_plan and "steps" in execution_plan:
                for step in execution_plan["steps"]:
                    agent_type = step["agent"]
                    action = step["action"]
                    inputs = step.get("inputs", {})

                    # 处理inputs中的引用（如"from_director"）
                    processed_inputs = self._resolve_inputs(inputs, current_context)

                    # 获取Agent并执行
                    agent = self.get_agent(agent_type)
                    if agent:
                        # 将inputs直接传递给agent，同时传递context
                        agent_response = await agent.process(
                            processed_inputs,
                            context=current_context,
                        )

                        # 记录结果
                        results[f"{agent_type}_{action}"] = agent_response.data

                        # 更新上下文（将agent_type作为key，方便后续引用）
                        current_context[agent_type] = agent_response.data

                        # 如果失败，中断执行
                        if not agent_response.success:
                            return {
                                "success": False,
                                "error": agent_response.error,
                                "failed_at": step,
                                "results": results,
                            }

            return {
                "success": True,
                "results": results,
                "final_context": current_context,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"工作流执行失败: {str(e)}",
                "results": results if 'results' in locals() else {},
            }

    def _resolve_inputs(
        self,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        解析输入中的引用

        Args:
            inputs: 输入数据
            context: 上下文

        Returns:
            解析后的输入数据
        """
        resolved = {}

        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("from_"):
                # 从上下文中获取数据
                source_key = value.replace("from_", "")

                # 首先尝试直接从context获取（按agent_type）
                if source_key in context:
                    source_data = context[source_key]
                    # 如果是dict，直接合并到resolved
                    if isinstance(source_data, dict):
                        resolved.update(source_data)
                    else:
                        resolved[key] = source_data
                else:
                    # 尝试从嵌套的agent结果中获取
                    for agent_data in context.values():
                        if isinstance(agent_data, dict) and source_key in agent_data:
                            resolved[key] = agent_data[source_key]
                            break
            else:
                resolved[key] = value

        return resolved

    async def route_message(
        self,
        message: AgentMessage,
    ) -> AgentResponse:
        """
        路由消息到对应的Agent

        Args:
            message: 消息

        Returns:
            Agent响应
        """
        receiver = message.receiver
        agent = self.get_agent(receiver)

        if not agent:
            return AgentResponse(
                success=False,
                error=f"Agent {receiver} 不存在",
            )

        # 记录消息
        self.conversation_history.append(message)

        # 转发给目标Agent处理
        response = await agent.receive_message(message)

        return response

    async def agent_collaborate(
        self,
        agents: List[str],
        task: str,
        initial_data: Dict[str, Any],
    ) -> List[AgentResponse]:
        """
        多Agent协作完成任务

        Args:
            agents: 参与协作的Agent列表
            task: 任务描述
            initial_data: 初始数据

        Returns:
            所有Agent的响应
        """
        responses = []
        current_data = initial_data

        for agent_type in agents:
            agent = self.get_agent(agent_type)
            if agent:
                response = await agent.process(current_data)
                responses.append(response)

                # 更新数据传递给下一个Agent
                if response.success and response.data:
                    current_data.update(response.data)

        return responses

    def get_conversation_history(self) -> List[AgentMessage]:
        """获取对话历史"""
        return self.conversation_history

    def clear_conversation_history(self):
        """清空对话历史"""
        self.conversation_history = []


# 全局Agent Manager实例
_agent_manager_v2: Optional[AgentManagerV2] = None


def get_agent_manager_v2() -> AgentManagerV2:
    """获取Agent Manager V2实例"""
    global _agent_manager_v2
    if _agent_manager_v2 is None:
        _agent_manager_v2 = AgentManagerV2()
    return _agent_manager_v2
