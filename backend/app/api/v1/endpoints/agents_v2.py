"""V2 Agent API端点 - AI导演团队"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.db.database import get_db
from app.models.conversation import ConversationMessage
from app.models.project import Project
from app.core.workflow_rules import WorkflowStage, get_next_actions
import uuid
from datetime import datetime

router = APIRouter()


@router.get("/workflow/actions/{stage}")
async def get_workflow_actions(
    stage: str,
    db: Session = Depends(get_db),
):
    """
    获取指定阶段的可执行操作

    Args:
        stage: 工作流阶段 (script, prompts, storyboard, frames, video, consistency)
        db: 数据库会话

    Returns:
        可执行的操作列表
    """
    try:
        # 验证阶段
        try:
            workflow_stage = WorkflowStage(stage)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的阶段: {stage}")

        # 获取可执行操作
        actions = get_next_actions(workflow_stage)

        return {
            "success": True,
            "stage": stage,
            "actions": actions,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取操作失败: {str(e)}")


@router.post("/chat")
async def chat_with_ai_team(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    与AI导演团队对话 - 直接调用剧本创作agent（智谱AI）

    Args:
        request: 包含project_id和message的请求
        db: 数据库会话

    Returns:
        AI响应和推荐操作
    """
    try:
        from app.services.zhipuai_service import get_zhipuai_service

        project_id = request.get("project_id")
        message_content = request.get("message", "")
        current_stage = request.get("current_stage", "script")  # 当前阶段

        if not project_id or not message_content:
            raise HTTPException(status_code=400, detail="缺少必要参数")

        # 验证项目存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 保存用户消息
        user_message = ConversationMessage(
            id=str(uuid.uuid4()),
            project_id=project_id,
            role="user",
            content=message_content,
            created_at=datetime.utcnow(),
        )
        db.add(user_message)

        # 获取对话历史
        conversation_history = db.query(ConversationMessage)\
            .filter(ConversationMessage.project_id == project_id)\
            .order_by(ConversationMessage.created_at.asc())\
            .limit(20)\
            .all()

        # 构建对话上下文
        context = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in conversation_history[:-1]  # 排除刚添加的用户消息
        ])

        # 系统提示词 - 剧本创作助手
        system_prompt = """你是一个专业的短剧创作助手。你的职责包括：

1. **剧本创作**：根据用户的创意创作完整的短剧剧本
2. **角色设计**：设计鲜明的角色性格和特征
3. **场景规划**：规划合适的场景和镜头
4. **对话优化**：优化角色对话，使其更自然生动

当用户提出创作需求时，请：
- 理解用户的核心创意和主题
- 询问必要的细节（如风格、时长、角色等）
- 创作结构完整的剧本（包含场景、对话、动作描述）
- 保持创作风格的一致性

**重要提示**：
- 当剧本创作完成后，明确告知用户"剧本创作完成"
- 当提示词优化完成后，明确告知用户"提示词优化完成"
- 当分镜设计完成后，明确告知用户"分镜设计完成"

请用友好、专业的语气回复。"""

        # 调用智谱AI
        zhipuai_service = get_zhipuai_service()
        ai_response = await zhipuai_service.chat_with_system_prompt(
            system_prompt=system_prompt,
            user_message=message_content,
            context=context if context else None,
            temperature=0.8,
        )

        # 保存AI回复
        assistant_message = ConversationMessage(
            id=str(uuid.uuid4()),
            project_id=project_id,
            role="assistant",
            content=ai_response,
            created_at=datetime.utcnow(),
        )
        db.add(assistant_message)
        db.commit()

        # 智能检测下一阶段
        detected_stage = current_stage
        if "剧本创作完成" in ai_response or "剧本已完成" in ai_response:
            detected_stage = "prompts"
        elif "提示词优化完成" in ai_response or "提示词已优化" in ai_response:
            detected_stage = "storyboard"
        elif "分镜设计完成" in ai_response or "分镜已完成" in ai_response:
            detected_stage = "frames"

        # 获取推荐操作
        try:
            workflow_stage = WorkflowStage(detected_stage)
            next_actions = get_next_actions(workflow_stage)
        except ValueError:
            next_actions = []

        return {
            "success": True,
            "message": ai_response,
            "project_id": project_id,
            "current_stage": detected_stage,
            "next_actions": next_actions,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.get("/agents")
async def list_agents():
    """
    列出所有可用的Agent

    Returns:
        Agent列表
    """
    return {
        "agents": [
            {
                "id": "script-writer",
                "name": "剧本创作",
                "description": "负责剧本创作、角色设计和对话优化",
                "model": "39e7431665754cc08fe332777f7968e7.ei00hbZ9bAYzSvEW"
            }
        ]
    }
