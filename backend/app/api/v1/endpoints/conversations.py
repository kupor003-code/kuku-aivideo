"""对话API端点"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.conversation import SendMessageRequest, MessageResponse
from app.models.conversation import ConversationMessage
from app.models.project import Project
from app.db.database import get_db
# V2: 不再需要agent_service，改用agents_v2
import uuid
from datetime import datetime

router = APIRouter()


@router.get("/{project_id}/messages", response_model=List[MessageResponse])
async def get_messages(project_id: str, db: Session = Depends(get_db)):
    """
    获取项目的所有对话消息

    Args:
        project_id: 项目ID
        db: 数据库会话

    Returns:
        消息列表
    """
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 获取消息
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.project_id == project_id
    ).order_by(ConversationMessage.created_at).all()

    return [
        MessageResponse(
            id=msg.id,
            project_id=msg.project_id,
            role=msg.role,
            content=msg.content,
            agent_type=msg.agent_type,
            agent_name=msg.agent_name,
            related_node_id=msg.related_node_id,
            related_node_type=msg.related_node_type,
            meta=msg.meta,
            created_at=msg.created_at.isoformat(),
        )
        for msg in messages
    ]


@router.post("/{project_id}/messages", response_model=MessageResponse)
async def send_message(
    project_id: str,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
):
    """
    发送消息

    Args:
        project_id: 项目ID
        request: 消息内容
        db: 数据库会话

    Returns:
        创建的消息
    """
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 创建消息
    message = ConversationMessage(
        id=str(uuid.uuid4()),
        project_id=project_id,
        role=request.role,
        content=request.content,
        agent_type=request.agent_type,
        agent_name=request.agent_name,
        related_node_id=request.related_node_id,
        related_node_type=request.related_node_type,
        meta=request.meta,
        created_at=datetime.utcnow(),
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    # TODO: 如果是用户消息，触发AI Agent生成回复
    # if request.role == "user":
    #     # 异步调用AI Agent
    #     pass

    return MessageResponse(
        id=message.id,
        project_id=message.project_id,
        role=message.role,
        content=message.content,
        agent_type=message.agent_type,
        agent_name=message.agent_name,
        related_node_id=message.related_node_id,
        related_node_type=message.related_node_type,
        meta=message.meta,
        created_at=message.created_at.isoformat(),
    )


@router.delete("/{project_id}/messages/{message_id}")
async def delete_message(project_id: str, message_id: str, db: Session = Depends(get_db)):
    """
    删除消息

    Args:
        project_id: 项目ID
        message_id: 消息ID
        db: 数据库会话

    Returns:
        删除结果
    """
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 查找消息
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == message_id,
        ConversationMessage.project_id == project_id,
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    db.delete(message)
    db.commit()

    return {"message": "删除成功"}


@router.delete("/{project_id}/messages")
async def clear_conversation(project_id: str, db: Session = Depends(get_db)):
    """
    清空对话历史

    Args:
        project_id: 项目ID
        db: 数据库会话

    Returns:
        清空结果
    """
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 删除所有消息
    db.query(ConversationMessage).filter(
        ConversationMessage.project_id == project_id
    ).delete()

    db.commit()

    return {"message": "对话历史已清空"}
