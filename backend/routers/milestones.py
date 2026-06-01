"""一步(StepOne) · 用户自定义里程碑 + 复盘卡 · V3.0"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from database import get_db
from models import User, UserMilestone, Memory

router = APIRouter(prefix="/api/milestones", tags=["自定义里程碑"])


class CreateMilestoneRequest(BaseModel):
    user_id: int
    name: str
    verification: str = ""


class UpdateMilestoneRequest(BaseModel):
    user_id: int
    milestone_id: int
    status: str


class ReflectMilestoneRequest(BaseModel):
    user_id: int
    milestone_id: int
    reflection: str


@router.post("/create")
async def create_milestone(req: CreateMilestoneRequest, db: AsyncSession = Depends(get_db)):
    """用户自己创建里程碑"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="用户不存在")

    count_result = await db.execute(
        select(UserMilestone).where(UserMilestone.user_id == req.user_id)
    )
    sort_order = len(count_result.scalars().all())

    milestone = UserMilestone(
        user_id=req.user_id,
        name=req.name,
        verification=req.verification,
        sort_order=sort_order,
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)

    return {"success": True, "id": milestone.id, "name": milestone.name}


@router.get("/list/{user_id}")
async def list_milestones(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户所有里程碑"""
    result = await db.execute(
        select(UserMilestone).where(UserMilestone.user_id == user_id).order_by(UserMilestone.sort_order)
    )
    milestones = result.scalars().all()

    return {
        "milestones": [{
            "id": m.id,
            "name": m.name,
            "verification": m.verification,
            "status": m.status,
            "reflection": m.reflection,
            "reflection_date": m.reflection_date.isoformat() if m.reflection_date else None,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None,
            "sort_order": m.sort_order,
        } for m in milestones],
        "completed": sum(1 for m in milestones if m.status == "completed"),
        "total": len(milestones),
    }


@router.post("/update")
async def update_milestone(req: UpdateMilestoneRequest, db: AsyncSession = Depends(get_db)):
    """更新里程碑状态"""
    result = await db.execute(select(UserMilestone).where(UserMilestone.id == req.milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="里程碑不存在")

    milestone.status = req.status
    if req.status == "completed":
        milestone.completed_at = datetime.utcnow()

    await db.commit()

    return {"success": True, "id": milestone.id, "status": req.status}


class DeleteMilestoneRequest(BaseModel):
    user_id: int
    milestone_id: int


@router.post("/delete")
async def delete_milestone(req: DeleteMilestoneRequest, db: AsyncSession = Depends(get_db)):
    """删除里程碑"""
    result = await db.execute(select(UserMilestone).where(
        UserMilestone.id == req.milestone_id,
        UserMilestone.user_id == req.user_id,
    ))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="里程碑不存在")

    await db.delete(milestone)
    await db.commit()

    return {"success": True, "message": "已删除"}


# ============ V3.0 里程碑复盘卡 ============

@router.post("/reflect")
async def reflect_milestone(req: ReflectMilestoneRequest, db: AsyncSession = Depends(get_db)):
    """完成里程碑后的复盘——这是V3.0的核心功能"""
    result = await db.execute(select(UserMilestone).where(UserMilestone.id == req.milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="里程碑不存在")

    milestone.reflection = req.reflection
    milestone.reflection_date = datetime.utcnow()

    # 创建记忆
    memory_content = f"完成了里程碑「{milestone.name}」并写下复盘：{req.reflection[:200]}"
    db.add(Memory(
        user_id=req.user_id,
        memory_type="milestone",
        content=memory_content,
        importance=3,
    ))

    await db.commit()

    return {"success": True, "message": "复盘已保存。这是你成长路上的一步，值得被记住。"}


@router.get("/reflect/{milestone_id}")
async def get_reflection(milestone_id: int, db: AsyncSession = Depends(get_db)):
    """获取某个里程碑的复盘内容"""
    result = await db.execute(select(UserMilestone).where(UserMilestone.id == milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="里程碑不存在")

    return {
        "id": milestone.id,
        "name": milestone.name,
        "reflection": milestone.reflection,
        "reflection_date": milestone.reflection_date.isoformat() if milestone.reflection_date else None,
    }
