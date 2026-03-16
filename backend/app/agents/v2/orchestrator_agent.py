"""Orchestrator Agent - 总控Agent"""
from typing import Dict, Any, Optional, List
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse


class OrchestratorAgent(BaseAgentV2):
    """
    Orchestrator Agent - AI总控
    负责解析用户需求、生成执行计划、调度其他Agent
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "orchestrator"
        self.agent_name = "AI总控"
        self.description = "负责解析用户需求、生成执行计划、调度其他Agent协作完成视频创作"
        self.capabilities = [
            "understand_user_intent",
            "create_execution_plan",
            "coordinate_agents",
            "track_progress",
            "handle_errors",
        ]

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入"""
        required_fields = ["user_input"]
        return all(field in input_data for field in required_fields)

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        处理用户输入，生成执行计划

        Args:
            input_data: 包含user_input的用户输入
            context: 上下文

        Returns:
            AgentResponse: 执行计划
        """
        try:
            user_input = input_data.get("user_input", "")

            # 1. 理解用户意图
            intent = await self._understand_intent(user_input)

            # 2. 生成执行计划
            execution_plan = await self._create_execution_plan(intent)

            # 3. 确定第一个执行的Agent
            first_agent = execution_plan["steps"][0]["agent"] if execution_plan["steps"] else None

            return AgentResponse(
                success=True,
                data={
                    "intent": intent,
                    "execution_plan": execution_plan,
                    "user_input": user_input,
                },
                message=f"我理解了你的创意：{user_input}。我将按照以下计划执行：",
                next_agent=first_agent,
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"总控处理失败: {str(e)}",
                message="抱歉，我遇到了一些问题",
            )

    async def _understand_intent(self, user_input: str) -> Dict[str, Any]:
        """
        理解用户意图

        Args:
            user_input: 用户输入

        Returns:
            意图分析结果
        """
        # 简化实现：实际应该调用LLM
        intent = {
            "type": "create_video",
            "topic": user_input,
            "keywords": self._extract_keywords(user_input),
            "style": "cinematic",
            "duration": "short",
        }
        return intent

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简化实现
        return [word for word in text.split() if len(word) > 1]

    async def _create_execution_plan(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建执行计划

        Args:
            intent: 用户意图

        Returns:
            执行计划
        """
        plan = {
            "overview": f"创作关于'{intent['topic']}'的视频",
            "steps": [
                {
                    "order": 1,
                    "agent": "director",
                    "action": "develop_creative_concept",
                    "description": "AI导演：开发创意概念和剧情",
                    "inputs": {"topic": intent["topic"]},
                },
                {
                    "order": 2,
                    "agent": "producer",
                    "action": "create_prompts",
                    "description": "AI制片：根据创意创作提示词",
                    "inputs": {"creative_concept": "from_director"},
                },
                {
                    "order": 3,
                    "agent": "storyboard",
                    "action": "generate_storyboard",
                    "description": "AI分镜：根据提示词生成分镜",
                    "inputs": {"prompts": "from_producer"},
                },
                {
                    "order": 4,
                    "agent": "consistency",
                    "action": "check_consistency",
                    "description": "AI审校：检查视觉一致性",
                    "inputs": {"storyboard": "from_storyboard"},
                },
                {
                    "order": 5,
                    "agent": "video",
                    "action": "generate_video",
                    "description": "AI视频：根据分镜生成视频",
                    "inputs": {"storyboard": "from_storyboard"},  # 从Storyboard获取，不是从Consistency
                },
            ],
            "estimated_duration": "10-15分钟",
        }
        return plan

    async def coordinate_agents(
        self,
        execution_plan: Dict[str, Any],
        agent_manager,
    ) -> Dict[str, Any]:
        """
        协调各个Agent执行计划

        Args:
            execution_plan: 执行计划
            agent_manager: Agent管理器

        Returns:
            执行结果
        """
        results = {}
        current_context = {}

        for step in execution_plan["steps"]:
            agent_type = step["agent"]
            agent = agent_manager.get_agent(agent_type)

            if agent:
                result = await agent.process(
                    {"action": step["action"], "inputs": step["inputs"]},
                    context=current_context,
                )

                results[f"{agent_type}_{step['action']}"] = result.data

                if not result.success:
                    # 处理错误
                    return {
                        "success": False,
                        "error": result.error,
                        "failed_at": step,
                        "results": results,
                    }

                # 更新上下文，传递给下一个Agent
                if result.data:
                    current_context.update(result.data)

        return {"success": True, "results": results}
