"""
Workflow Executor - 工作流执行引擎

这是系统的核心执行引擎，负责：
1. 执行 Orchestrator 生成的执行计划
2. 管理节点依赖关系
3. 调度 Agent 执行
4. 更新 Canvas 状态
5. 处理错误和重试
6. 维护执行上下文

WorkflowExecutor 是连接 Orchestrator 和各个 Agent 的桥梁。
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.agents.v2.orchestrator_agent_v2 import OrchestratorAgentV2
from app.agents.v2.script_agent_v2 import ScriptAgentV2
from app.agents.v2.document_parser_agent_v2 import DocumentParserAgentV2
from app.agents.v2.frame_agent_v2 import FrameAgentV2
from app.agents.v2.consistency_agent_v2 import ConsistencyAgentV2
from app.agents.v2.base_agent import AgentResponse


class WorkflowExecutionState:
    """工作流执行状态"""

    def __init__(
        self,
        project_id: str,
        execution_plan: Dict[str, Any],
    ):
        self.project_id = project_id
        self.execution_plan = execution_plan
        self.current_step_index = 0
        self.completed_steps = []
        self.failed_steps = []
        self.execution_context = {}
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def current_step(self) -> Optional[Dict[str, Any]]:
        """获取当前步骤"""
        if self.current_step_index < len(self.execution_plan["steps"]):
            return self.execution_plan["steps"][self.current_step_index]
        return None

    @property
    def is_completed(self) -> bool:
        """是否完成"""
        return self.current_step_index >= len(self.execution_plan["steps"])

    @property
    def is_failed(self) -> bool:
        """是否失败"""
        return len(self.failed_steps) > 0

    @property
    def progress(self) -> float:
        """进度百分比"""
        total_steps = len(self.execution_plan["steps"])
        if total_steps == 0:
            return 100.0
        return (len(self.completed_steps) / total_steps) * 100

    def advance_step(self):
        """前进一步"""
        self.current_step_index += 1
        self.updated_at = datetime.utcnow()

    def add_completed_step(self, step: Dict[str, Any], result: Dict[str, Any]):
        """添加已完成步骤"""
        self.completed_steps.append({
            "step": step,
            "result": result,
            "completed_at": datetime.utcnow().isoformat(),
        })
        self.updated_at = datetime.utcnow()

    def add_failed_step(self, step: Dict[str, Any], error: str):
        """添加失败步骤"""
        self.failed_steps.append({
            "step": step,
            "error": error,
            "failed_at": datetime.utcnow().isoformat(),
        })
        self.updated_at = datetime.utcnow()

    def update_context(self, data: Dict[str, Any]):
        """更新执行上下文"""
        self.execution_context.update(data)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "project_id": self.project_id,
            "execution_plan": self.execution_plan,
            "current_step_index": self.current_step_index,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "execution_context": self.execution_context,
            "is_completed": self.is_completed,
            "is_failed": self.is_failed,
            "progress": self.progress,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class WorkflowExecutor:
    """
    Workflow Executor - 工作流执行引擎

    职责：
    - 执行工作流计划
    - 调度 Agent
    - 管理状态
    - 处理错误
    """

    # Agent 注册表
    AGENTS = {
        "orchestrator": OrchestratorAgentV2,
        "document_parser": DocumentParserAgentV2,
        "script": ScriptAgentV2,
        "frame": FrameAgentV2,
        "consistency": ConsistencyAgentV2,
        # TODO: 添加其他 Agent
        # "storyboard": StoryboardAgentV2,
        # "video": VideoAgentV2,
    }

    def __init__(self):
        self._executions: Dict[str, WorkflowExecutionState] = {}
        self._agents: Dict[str, Any] = {}

    def _get_or_create_agent(self, agent_type: str) -> Any:
        """获取或创建 Agent 实例"""
        if agent_type not in self._agents:
            agent_class = self.AGENTS.get(agent_type)
            if not agent_class:
                raise ValueError(f"Unknown agent type: {agent_type}")
            self._agents[agent_type] = agent_class()

        return self._agents[agent_type]

    async def execute_plan(
        self,
        project_id: str,
        execution_plan: Dict[str, Any],
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        执行工作流计划

        Args:
            project_id: 项目ID
            execution_plan: 执行计划
            initial_context: 初始上下文

        Returns:
            执行结果
        """
        # 创建执行状态
        execution_state = WorkflowExecutionState(
            project_id=project_id,
            execution_plan=execution_plan,
        )

        # 初始化上下文
        if initial_context:
            execution_state.update_context(initial_context)

        # 保存执行状态
        self._executions[project_id] = execution_state

        try:
            # 逐步执行
            while not execution_state.is_completed and not execution_state.is_failed:
                # 获取当前步骤
                step = execution_state.current_step
                if not step:
                    break

                # 执行步骤
                result = await self._execute_step(
                    project_id=project_id,
                    step=step,
                    context=execution_state.execution_context,
                )

                if result["success"]:
                    # 步骤成功
                    execution_state.add_completed_step(step, result)
                    execution_state.update_context(result.get("data", {}))
                    execution_state.advance_step()
                else:
                    # 步骤失败
                    execution_state.add_failed_step(step, result.get("error"))
                    break

            # 返回最终结果
            return {
                "success": execution_state.is_completed and not execution_state.is_failed,
                "execution_state": execution_state.to_dict(),
                "project_id": project_id,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_state": execution_state.to_dict(),
                "project_id": project_id,
            }

    async def _execute_step(
        self,
        project_id: str,
        step: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        执行单个步骤

        Args:
            project_id: 项目ID
            step: 步骤信息
            context: 执行上下文

        Returns:
            执行结果
        """
        agent_type = step["agent"]
        action = step["action"]
        inputs = step.get("inputs", {})

        try:
            # 获取 Agent
            agent = self._get_or_create_agent(agent_type)

            # 解析 inputs（处理 from_previous 等引用）
            resolved_inputs = self._resolve_inputs(inputs, context)

            # 调用 Agent
            response: AgentResponse = await agent.process(
                input_data={
                    "action": action,
                    "inputs": resolved_inputs,
                    "project_id": project_id,
                },
                context=context,
            )

            # 返回结果
            return {
                "success": response.success,
                "data": response.data,
                "error": response.error,
                "message": response.message,
                "next_agent": response.next_agent,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": agent_type,
                "action": action,
            }

    def _resolve_inputs(
        self,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        解析输入（处理引用）

        Args:
            inputs: 输入数据
            context: 上下文

        Returns:
            解析后的输入
        """
        resolved = {}

        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("from_"):
                # 处理引用：from_previous, from_user, from_project 等
                reference_key = value.replace("from_", "")
                if reference_key == "previous":
                    # 从上下文中获取上一个节点的输出
                    resolved[key] = context
                elif reference_key == "user":
                    # 从用户输入获取（应该在 context 中）
                    resolved[key] = context.get("user_input", "")
                elif reference_key == "project":
                    # 从项目获取（ TODO: 实现项目数据获取）
                    resolved[key] = {}
                elif reference_key in context:
                    resolved[key] = context[reference_key]
                else:
                    resolved[key] = value
            else:
                resolved[key] = value

        return resolved

    def get_execution_state(self, project_id: str) -> Optional[WorkflowExecutionState]:
        """
        获取执行状态

        Args:
            project_id: 项目ID

        Returns:
            执行状态
        """
        return self._executions.get(project_id)

    def cancel_execution(self, project_id: str) -> bool:
        """
        取消执行

        Args:
            project_id: 项目ID

        Returns:
            是否成功取消
        """
        if project_id in self._executions:
            # TODO: 实现真正的取消逻辑（需要支持异步任务的取消）
            del self._executions[project_id]
            return True
        return False

    async def execute_step(
        self,
        project_id: str,
        step: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        执行单个步骤（用于手动执行）

        Args:
            project_id: 项目ID
            step: 步骤信息
            context: 上下文

        Returns:
            执行结果
        """
        return await self._execute_step(project_id, step, context)


# 全局单例
workflow_executor = WorkflowExecutor()
