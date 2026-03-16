"""
Orchestrator Agent V2 - 中心调度 Agent

这是系统的核心 Agent，负责：
1. 理解用户意图（使用 LLM）
2. 生成执行计划
3. 调度其他 Agent 执行
4. 管理工作流图
5. 维护项目上下文
6. 处理错误和重试

这个 Agent 是不可替换的，是系统的核心大脑。
"""

import json
from typing import Dict, Any, Optional, List
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse
from app.services.zhipuai_service import get_zhipuai_service


class OrchestratorAgentV2(BaseAgentV2):
    """
    Orchestrator Agent V2 - 中心调度 Agent

    职责：
    - 理解用户意图
    - 生成执行计划
    - 调度其他 Agent
    - 管理工作流状态
    """

    # 工作流主链路（固定顺序）
    MAIN_WORKFLOW = [
        "document_parser",  # 文档解析
        "script",           # 剧本创作
        "storyboard",       # 分镜拆解
        "frame",            # 首尾帧生成
        "video",            # 视频生成
        "consistency",      # 一致性检查
    ]

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
            "manage_workflow",
        ]
        self.llm_service = get_zhipuai_service()

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
            context: 上下文（包含项目信息、当前状态等）

        Returns:
            AgentResponse: 执行计划和下一步指令
        """
        try:
            user_input = input_data.get("user_input", "")
            project_id = input_data.get("project_id")
            current_stage = context.get("current_stage") if context else None

            # 1. 理解用户意图（使用 LLM）
            intent = await self._understand_intent_llm(
                user_input,
                project_id,
                current_stage,
                context
            )

            # 2. 分析当前项目状态
            project_status = await self._analyze_project_status(project_id, context)

            # 3. 生成执行计划
            execution_plan = await self._create_execution_plan(
                intent,
                project_status,
                current_stage
            )

            # 4. 确定第一个执行的Agent
            first_step = execution_plan["steps"][0] if execution_plan["steps"] else None
            first_agent = first_step["agent"] if first_step else None

            return AgentResponse(
                success=True,
                data={
                    "intent": intent,
                    "execution_plan": execution_plan,
                    "project_status": project_status,
                    "user_input": user_input,
                },
                message=self._generate_user_message(intent, execution_plan),
                next_agent=first_agent,
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"总控处理失败: {str(e)}",
                message="抱歉，我遇到了一些问题，请稍后再试。",
            )

    async def _understand_intent_llm(
        self,
        user_input: str,
        project_id: Optional[str],
        current_stage: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        使用 LLM 理解用户意图

        Args:
            user_input: 用户输入
            project_id: 项目ID
            current_stage: 当前阶段
            context: 上下文

        Returns:
            意图分析结果
        """
        system_prompt = """你是一个AI短剧创作平台的总控助手。你的任务是理解用户的创作意图，并提取关键信息。

请分析用户输入，返回JSON格式的意图分析，包含以下字段：
{
  "task_type": "任务类型（create_video/modify_script/regenerate_video/change_model/ask_question）",
  "topic": "创作主题或需求",
  "has_document": "是否提供了文档（true/false）",
  "document_type": "文档类型（pdf/docx/txt/none）",
  "style_preference": "风格偏好（cinematic/anime/documentary/commercial等）",
  "duration_preference": "时长偏好（short/medium/long）",
  "specific_requirements": "具体要求列表",
  "urgency": "紧急程度（normal/high）",
  "confidence": "理解置信度（0-1）"
}

只返回JSON，不要有其他内容。"""

        # 构建上下文信息
        context_info = ""
        if project_id:
            context_info += f"项目ID: {project_id}\n"
        if current_stage:
            context_info += f"当前阶段: {current_stage}\n"
        if context:
            context_info += f"项目状态: {context.get('project_status', {})}\n"

        user_message = f"上下文信息：\n{context_info}\n\n用户输入：{user_input}"

        try:
            response = await self.llm_service.chat_with_system_prompt(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.3,  # 使用较低温度以获得稳定的结构化输出
            )

            # 解析 JSON
            intent = json.loads(response)
            return intent

        except Exception as e:
            # LLM 调用失败时，使用规则解析
            return self._understand_intent_fallback(user_input, context)

    def _understand_intent_fallback(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        规则解析意图（LLM 失败时的回退方案）

        Args:
            user_input: 用户输入
            context: 上下文

        Returns:
            意图分析结果
        """
        # 简单的关键词匹配
        task_type = "create_video"
        if any(word in user_input for word in ["修改", "调整", "改"]):
            task_type = "modify_script"
        elif any(word in user_input for word in ["重新生成", "再生成"]):
            task_type = "regenerate_video"
        elif any(word in user_input for word in ["模型", "换成"]):
            task_type = "change_model"
        elif any(word in user_input for word in ["怎么", "如何", "什么"]):
            task_type = "ask_question"

        return {
            "task_type": task_type,
            "topic": user_input[:100],  # 截取前100个字符
            "has_document": False,
            "document_type": "none",
            "style_preference": "cinematic",
            "duration_preference": "short",
            "specific_requirements": [],
            "urgency": "normal",
            "confidence": 0.5,
        }

    async def _analyze_project_status(
        self,
        project_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析项目当前状态

        Args:
            project_id: 项目ID
            context: 上下文

        Returns:
            项目状态分析
        """
        if not project_id:
            return {
                "exists": False,
                "current_stage": "init",
                "completed_stages": [],
                "next_stage": "document_parser",
            }

        # 从 context 中获取项目状态
        if context and "project_status" in context:
            return context["project_status"]

        # 默认状态
        return {
            "exists": True,
            "current_stage": "unknown",
            "completed_stages": [],
            "next_stage": "document_parser",
        }

    async def _create_execution_plan(
        self,
        intent: Dict[str, Any],
        project_status: Dict[str, Any],
        current_stage: Optional[str]
    ) -> Dict[str, Any]:
        """
        创建执行计划

        Args:
            intent: 用户意图
            project_status: 项目状态
            current_stage: 当前阶段

        Returns:
            执行计划
        """
        task_type = intent.get("task_type", "create_video")

        # 根据任务类型生成不同的执行计划
        if task_type == "create_video":
            return self._create_plan_for_new_project(intent, project_status)
        elif task_type == "modify_script":
            return self._create_plan_for_modify(intent, project_status)
        elif task_type == "regenerate_video":
            return self._create_plan_for_regenerate(intent, project_status)
        elif task_type == "change_model":
            return self._create_plan_for_change_model(intent, project_status)
        else:
            return self._create_plan_for_question(intent, project_status)

    def _create_plan_for_new_project(
        self,
        intent: Dict[str, Any],
        project_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建新项目的执行计划"""
        has_document = intent.get("has_document", False)

        steps = []

        # 根据是否有文档决定第一步
        if has_document:
            steps.append({
                "order": 1,
                "agent": "document_parser",
                "action": "parse_document",
                "description": "解析文档，提取剧情信息",
                "inputs": {"document": "from_user"},
            })
        else:
            steps.append({
                "order": 1,
                "agent": "script",
                "action": "generate_script",
                "description": "根据创意生成剧本",
                "inputs": {"creative_idea": intent.get("topic")},
            })

        # 后续步骤
        steps.extend([
            {
                "order": len(steps) + 1,
                "agent": "script",
                "action": "generate_storyboard",
                "description": "生成分镜脚本和镜头拆解",
                "inputs": {"script": "from_previous"},
            },
            {
                "order": len(steps) + 1,
                "agent": "frame",
                "action": "generate_frames",
                "description": "生成每个镜头的首帧和尾帧",
                "inputs": {"storyboard": "from_previous"},
            },
            {
                "order": len(steps) + 1,
                "agent": "frame",
                "action": "generate_videos",
                "description": "生成视频片段",
                "inputs": {"frames": "from_previous"},
            },
            {
                "order": len(steps) + 1,
                "agent": "consistency",
                "action": "check_consistency",
                "description": "检查视觉一致性",
                "inputs": {"videos": "from_previous"},
            },
        ])

        return {
            "task_type": "create_video",
            "overview": f"创作关于'{intent.get('topic', '用户创意')}'的短剧视频",
            "steps": steps,
            "estimated_duration": self._estimate_duration(steps),
            "requirements": intent.get("specific_requirements", []),
        }

    def _create_plan_for_modify(
        self,
        intent: Dict[str, Any],
        project_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建修改剧本的执行计划"""
        return {
            "task_type": "modify_script",
            "overview": f"修改剧本：{intent.get('topic', '')}",
            "steps": [
                {
                    "order": 1,
                    "agent": "script",
                    "action": "modify_script",
                    "description": "根据用户反馈修改剧本",
                    "inputs": {"feedback": intent.get("topic")},
                }
            ],
            "estimated_duration": "2-3分钟",
            "requirements": intent.get("specific_requirements", []),
        }

    def _create_plan_for_regenerate(
        self,
        intent: Dict[str, Any],
        project_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建重新生成视频的执行计划"""
        return {
            "task_type": "regenerate_video",
            "overview": "重新生成视频",
            "steps": [
                {
                    "order": 1,
                    "agent": "video",
                    "action": "regenerate_videos",
                    "description": "重新生成视频片段",
                    "inputs": {"storyboard": "from_project"},
                }
            ],
            "estimated_duration": "5-10分钟",
            "requirements": intent.get("specific_requirements", []),
        }

    def _create_plan_for_change_model(
        self,
        intent: Dict[str, Any],
        project_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建切换模型的执行计划"""
        return {
            "task_type": "change_model",
            "overview": "切换生成模型",
            "steps": [
                {
                    "order": 1,
                    "agent": "system",
                    "action": "update_provider_config",
                    "description": "更新模型配置",
                    "inputs": {"new_model": intent.get("topic")},
                }
            ],
            "estimated_duration": "立即完成",
            "requirements": intent.get("specific_requirements", []),
        }

    def _create_plan_for_question(
        self,
        intent: Dict[str, Any],
        project_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建回答问题的执行计划"""
        return {
            "task_type": "ask_question",
            "overview": "回答用户问题",
            "steps": [],
            "estimated_duration": "立即完成",
            "requirements": intent.get("specific_requirements", []),
        }

    def _estimate_duration(self, steps: List[Dict[str, Any]]) -> str:
        """估算执行时长"""
        # 简单估算：每步2-3分钟
        step_count = len(steps)
        if step_count <= 2:
            return "2-5分钟"
        elif step_count <= 4:
            return "5-10分钟"
        else:
            return "10-15分钟"

    def _generate_user_message(
        self,
        intent: Dict[str, Any],
        execution_plan: Dict[str, Any]
    ) -> str:
        """生成给用户的消息"""
        task_type = intent.get("task_type", "create_video")

        if task_type == "create_video":
            return (
                f"我理解了你的创意：{intent.get('topic', '')}。\n\n"
                f"我将按照以下计划执行：\n"
                + "\n".join([
                    f"{i+1}. {step['description']}"
                    for i, step in enumerate(execution_plan["steps"])
                ])
                + f"\n\n预计用时：{execution_plan['estimated_duration']}"
            )
        elif task_type == "modify_script":
            return f"好的，我将根据你的反馈修改剧本。"
        elif task_type == "regenerate_video":
            return f"好的，我将重新生成视频。"
        elif task_type == "change_model":
            return f"好的，我将切换模型配置。"
        else:
            return execution_plan.get("overview", "我明白了，让我来帮你。")

    async def coordinate_agents(
        self,
        execution_plan: Dict[str, Any],
        agent_manager,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        协调各个Agent执行计划

        Args:
            execution_plan: 执行计划
            agent_manager: Agent管理器
            context: 上下文

        Returns:
            执行结果
        """
        results = {}
        current_context = context or {}

        for step in execution_plan["steps"]:
            agent_type = step["agent"]
            action = step["action"]

            # 获取 Agent
            agent = agent_manager.get_agent(agent_type)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent {agent_type} not found",
                    "failed_at": step,
                    "results": results,
                }

            # 执行 Agent
            try:
                result = await agent.process(
                    {"action": action, "inputs": step["inputs"]},
                    context=current_context,
                )

                results[f"{agent_type}_{action}"] = result.data

                if not result.success:
                    return {
                        "success": False,
                        "error": result.error,
                        "failed_at": step,
                        "results": results,
                    }

                # 更新上下文
                if result.data:
                    current_context.update(result.data)

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "failed_at": step,
                    "results": results,
                }

        return {
            "success": True,
            "results": results,
            "final_context": current_context,
        }
