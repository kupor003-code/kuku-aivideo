"""
演示案例 API 端点
用于保存和获取真实生成的演示内容
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel

from app.db.database import get_db
from app.models.demo_case import DemoCase

router = APIRouter()


class DemoCaseCreate(BaseModel):
    """创建演示案例"""
    title: str
    description: Optional[str] = None
    script: str
    total_duration: float
    fragments: list
    total_images: int = 0
    total_videos: int = 0


class DemoCaseResponse(BaseModel):
    """演示案例响应"""
    id: str
    title: str
    description: Optional[str]
    script: str
    total_duration: float
    fragments: list
    total_images: int
    total_videos: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/demo-cases", response_model=DemoCaseResponse)
async def create_demo_case(
    case_data: DemoCaseCreate,
    db: Session = Depends(get_db),
):
    """
    创建新的演示案例

    用于保存真实生成的演示内容
    """
    try:
        # 生成唯一ID
        case_id = f"demo-{uuid.uuid4().hex[:8]}"

        demo_case = DemoCase(
            id=case_id,
            title=case_data.title,
            description=case_data.description,
            script=case_data.script,
            total_duration=case_data.total_duration,
            fragments=case_data.fragments,
            total_images=case_data.total_images,
            total_videos=case_data.total_videos,
            is_public=1,  # 默认公开
        )

        db.add(demo_case)
        db.commit()
        db.refresh(demo_case)

        return demo_case

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建演示案例失败: {str(e)}")


@router.get("/demo-cases", response_model=List[DemoCaseResponse])
async def list_demo_cases(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    获取演示案例列表

    按创建时间倒序排列
    """
    try:
        cases = db.query(DemoCase)\
            .filter(DemoCase.is_public == 1)\
            .order_by(DemoCase.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        return cases

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取演示案例失败: {str(e)}")


@router.get("/demo-cases/latest", response_model=DemoCaseResponse)
async def get_latest_demo_case(db: Session = Depends(get_db)):
    """
    获取最新的演示案例

    用于主页展示
    """
    try:
        case = db.query(DemoCase)\
            .filter(DemoCase.is_public == 1)\
            .order_by(DemoCase.created_at.desc())\
            .first()

        if not case:
            raise HTTPException(status_code=404, detail="暂无演示案例")

        return case

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取演示案例失败: {str(e)}")


@router.get("/demo-cases/{case_id}", response_model=DemoCaseResponse)
async def get_demo_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    """
    获取单个演示案例详情
    """
    try:
        case = db.query(DemoCase)\
            .filter(DemoCase.id == case_id)\
            .filter(DemoCase.is_public == 1)\
            .first()

        if not case:
            raise HTTPException(status_code=404, detail="演示案例不存在")

        return case

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取演示案例失败: {str(e)}")


@router.put("/demo-cases/{case_id}", response_model=DemoCaseResponse)
async def update_demo_case(
    case_id: str,
    case_data: DemoCaseCreate,
    db: Session = Depends(get_db),
):
    """
    更新演示案例

    用于在继续生成后更新案例内容
    """
    try:
        case = db.query(DemoCase).filter(DemoCase.id == case_id).first()

        if not case:
            raise HTTPException(status_code=404, detail="演示案例不存在")

        # 更新字段
        case.title = case_data.title
        case.description = case_data.description
        case.script = case_data.script
        case.total_duration = case_data.total_duration
        case.fragments = case_data.fragments
        case.total_images = case_data.total_images
        case.total_videos = case_data.total_videos
        case.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(case)

        return case

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新演示案例失败: {str(e)}")
