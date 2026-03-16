"""
Workflow API 端点 - 工作流执行

这个模块提供工作流执行的 API 端点，用于：
1. 执行工作流计划
2. 查询执行状态
3. 取消执行
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.db.database import get_db
from app.workflows.executor import workflow_executor
from app.agents.v2.orchestrator_agent_v2 import OrchestratorAgentV2
from app.models.project import Project
import uuid

router = APIRouter()


@router.post("/execute")
async def execute_workflow(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    执行工作流

    请求体示例：
    {
        "project_id": "optional-project-id",
        "user_input": "用户输入的创意描述",
        "auto_execute": true  // 是否自动执行所有步骤
    }

    Returns:
        执行结果
    """
    try:
        user_input = request.get("user_input", "")
        project_id = request.get("project_id") or str(uuid.uuid4())
        auto_execute = request.get("auto_execute", False)

        if not user_input:
            raise HTTPException(status_code=400, detail="缺少 user_input")

        # 1. 使用 Orchestrator 理解意图并生成执行计划
        orchestrator = OrchestratorAgentV2()
        response = await orchestrator.process(
            input_data={
                "user_input": user_input,
                "project_id": project_id,
            },
            context={"project_id": project_id},
        )

        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)

        execution_plan = response.data.get("execution_plan")

        # 2. 如果不需要自动执行，直接返回计划
        if not auto_execute:
            return {
                "success": True,
                "project_id": project_id,
                "execution_plan": execution_plan,
                "message": response.message,
                "auto_execute": False,
            }

        # 3. 自动执行工作流
        result = await workflow_executor.execute_plan(
            project_id=project_id,
            execution_plan=execution_plan,
            initial_context={"user_input": user_input},
        )

        return {
            "success": result.get("success", False),
            "project_id": project_id,
            "execution_state": result.get("execution_state"),
            "message": "工作流执行完成" if result.get("success") else "工作流执行失败",
            "error": result.get("error"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行工作流失败: {str(e)}")


@router.get("/status/{project_id}")
async def get_workflow_status(project_id: str):
    """
    获取工作流执行状态

    Args:
        project_id: 项目ID

    Returns:
        执行状态
    """
    try:
        execution_state = workflow_executor.get_execution_state(project_id)

        if not execution_state:
            return {
                "success": False,
                "message": "没有找到执行记录",
                "project_id": project_id,
            }

        return {
            "success": True,
            "execution_state": execution_state.to_dict(),
            "project_id": project_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.post("/cancel/{project_id}")
async def cancel_workflow(project_id: str):
    """
    取消工作流执行

    Args:
        project_id: 项目ID

    Returns:
        取消结果
    """
    try:
        success = workflow_executor.cancel_execution(project_id)

        return {
            "success": success,
            "message": "已取消执行" if success else "取消失败",
            "project_id": project_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消失败: {str(e)}")


@router.post("/step/execute")
async def execute_step(
    request: Dict[str, Any],
):
    """
    执行单个步骤（用于手动执行）

    请求体示例：
    {
        "project_id": "project-id",
        "step": {
            "order": 1,
            "agent": "script",
            "action": "generate_script",
            "description": "...",
            "inputs": {...}
        },
        "context": {...}
    }

    Returns:
        执行结果
    """
    try:
        project_id = request.get("project_id")
        step = request.get("step")
        context = request.get("context", {})

        if not project_id or not step:
            raise HTTPException(status_code=400, detail="缺少必要参数")

        result = await workflow_executor.execute_step(
            project_id=project_id,
            step=step,
            context=context,
        )

        return {
            "success": result.get("success", False),
            "result": result,
            "project_id": project_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行步骤失败: {str(e)}")


@router.post("/plan/generate")
async def generate_execution_plan(
    request: Dict[str, Any],
):
    """
    生成执行计划（不执行）

    请求体示例：
    {
        "user_input": "用户输入的创意描述",
        "project_id": "optional-project-id"
    }

    Returns:
        执行计划
    """
    try:
        user_input = request.get("user_input", "")
        project_id = request.get("project_id")

        if not user_input:
            raise HTTPException(status_code=400, detail="缺少 user_input")

        # 使用 Orchestrator 生成执行计划
        orchestrator = OrchestratorAgentV2()
        response = await orchestrator.process(
            input_data={
                "user_input": user_input,
                "project_id": project_id,
            },
            context={"project_id": project_id} if project_id else None,
        )

        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)

        return {
            "success": True,
            "intent": response.data.get("intent"),
            "execution_plan": response.data.get("execution_plan"),
            "message": response.message,
            "next_agent": response.next_agent,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成计划失败: {str(e)}")
