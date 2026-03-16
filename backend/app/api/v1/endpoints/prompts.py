"""提示词API端点 - V2使用PromptVersion"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.schemas.prompt_schema import PromptCreate, PromptResponse
from app.models.prompt_version import PromptVersion as PromptModel  # V2: 使用PromptVersion
from app.models.project import Project
from app.db.database import get_db

router = APIRouter()


@router.post("/", response_model=PromptResponse)
async def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    """
    创建提示词

    Args:
        prompt: 提示词创建请求
        db: 数据库会话

    Returns:
        创建的提示词
    """
    try:
        # 验证项目是否存在
        project = db.query(Project).filter(Project.id == prompt.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 生成提示词ID
        prompt_id = str(uuid.uuid4())

        # 如果有父ID，获取父版本号
        version = 1
        if prompt.parent_id:
            parent = db.query(PromptModel).filter(PromptModel.id == prompt.parent_id).first()
            if parent:
                version = parent.version + 1

        db_prompt = PromptModel(
            id=prompt_id,
            project_id=prompt.project_id,
            type=prompt.type,
            content=prompt.content,
            version=version,
            parent_id=prompt.parent_id,
            source=prompt.source,
            meta=prompt.metadata,
            created_at=datetime.utcnow(),
        )

        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)

        return db_prompt

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建提示词失败: {str(e)}")


@router.get("/project/{project_id}", response_model=List[PromptResponse])
async def get_project_prompts(
    project_id: str,
    prompt_type: str = None,
    db: Session = Depends(get_db),
):
    """
    获取项目的所有提示词

    Args:
        project_id: 项目ID
        prompt_type: 提示词类型（可选）
        db: 数据库会话

    Returns:
        提示词列表
    """
    try:
        query = db.query(PromptModel).filter(PromptModel.project_id == project_id)

        if prompt_type:
            query = query.filter(PromptModel.type == prompt_type)

        prompts = query.order_by(PromptModel.created_at.desc()).all()

        return prompts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提示词列表失败: {str(e)}")


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: str, db: Session = Depends(get_db)):
    """
    获取提示词详情

    Args:
        prompt_id: 提示词ID
        db: 数据库会话

    Returns:
        提示词详情
    """
    try:
        prompt = db.query(PromptModel).filter(PromptModel.id == prompt_id).first()

        if not prompt:
            raise HTTPException(status_code=404, detail="提示词不存在")

        return prompt

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提示词失败: {str(e)}")
