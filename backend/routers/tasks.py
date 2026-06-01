"""每日微任务 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from database import get_db
from models import User, Milestone, MicroTask, WeeklySummary
from services.microtask_service import generate_daily_tasks
from services.roadmap_service import get_week_range

router = APIRouter(prefix="/api/tasks", tags=["每日微任务"])


class GenerateTasksRequest(BaseModel):
    user_id: int


class CompleteTaskRequest(BaseModel):
    task_id: int
    user_id: int


@router.post("/generate")
async def generate_tasks(req: GenerateTasksRequest, db: AsyncSession = Depends(get_db)):
    """为用户生成今日微任务"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    today = datetime.now().strftime("%Y-%m-%d")

    # 清除今日旧任务
    old_result = await db.execute(
        select(MicroTask).where(MicroTask.user_id == req.user_id, MicroTask.task_date == today)
    )
    for old in old_result.scalars().all():
        await db.delete(old)

    # 找当前在进行的里程碑
    ms_result = await db.execute(
        select(Milestone).where(Milestone.status == "in_progress").order_by(Milestone.id).limit(1)
    )
    current_milestone = ms_result.scalar_one_or_none()

    milestone_name = current_milestone.name if current_milestone else "通用学习"

    tasks = generate_daily_tasks(milestone_name)

    created = []
    for i, task in enumerate(tasks):
        mt = MicroTask(
            user_id=req.user_id,
            milestone_id=current_milestone.id if current_milestone else None,
            content=task["content"],
            estimated_minutes=task["estimated_minutes"],
            status="pending",
            task_date=today,
            sort_order=i,
        )
        db.add(mt)
        await db.flush()
        created.append({
            "id": mt.id,
            "content": mt.content,
            "estimated_minutes": mt.estimated_minutes,
            "status": mt.status,
        })

    await db.commit()

    return {
        "date": today,
        "milestone": milestone_name,
        "tasks": created,
        "total": len(created),
    }


@router.get("/today/{user_id}")
async def get_today_tasks(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取今日微任务"""
    today = datetime.now().strftime("%Y-%m-%d")
    result = await db.execute(
        select(MicroTask)
        .where(MicroTask.user_id == user_id, MicroTask.task_date == today)
        .order_by(MicroTask.sort_order)
    )
    tasks = result.scalars().all()

    if not tasks:
        return {"date": today, "tasks": [], "has_tasks": False}

    return {
        "date": today,
        "has_tasks": True,
        "tasks": [
            {
                "id": t.id,
                "content": t.content,
                "estimated_minutes": t.estimated_minutes,
                "status": t.status,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in tasks
        ],
        "completed": sum(1 for t in tasks if t.status == "completed"),
        "total": len(tasks),
    }


@router.post("/complete")
async def complete_task(req: CompleteTaskRequest, db: AsyncSession = Depends(get_db)):
    """完成任务打卡"""
    result = await db.execute(select(MicroTask).where(MicroTask.id == req.task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.status = "completed"
    task.completed_at = datetime.utcnow()
    await db.commit()

    # 计算今日完成数
    today = datetime.now().strftime("%Y-%m-%d")
    count_result = await db.execute(
        select(func.count()).select_from(MicroTask).where(
            MicroTask.user_id == req.user_id,
            MicroTask.task_date == today,
            MicroTask.status == "completed",
        )
    )
    completed_count = count_result.scalar() or 0

    # 计算连续打卡天数
    streak = await _calculate_streak(req.user_id, db)

    return {
        "success": True,
        "today_completed": completed_count,
        "streak": streak,
    }


async def _calculate_streak(user_id: int, db: AsyncSession) -> int:
    """计算连续打卡天数"""
    from sqlalchemy import distinct, desc
    result = await db.execute(
        select(distinct(MicroTask.task_date))
        .where(MicroTask.user_id == user_id, MicroTask.status == "completed")
        .order_by(desc(MicroTask.task_date))
        .limit(30)
    )
    dates = [row[0] for row in result.all()]

    if not dates:
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    streak = 0
    check_date = datetime.strptime(
        dates[0] if dates[0] >= today else today, "%Y-%m-%d"
    )

    for date_str in [today] + dates:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        if d == check_date or d == check_date:
            streak += 1
            check_date = check_date.replace(day=check_date.day - 1) if check_date.day > 1 else check_date
        else:
            break

    return streak


@router.get("/streak/{user_id}")
async def get_streak(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取打卡统计"""
    streak = await _calculate_streak(user_id, db)

    # 本周完成数
    week_start, week_end = get_week_range()
    week_result = await db.execute(
        select(func.count()).select_from(MicroTask).where(
            MicroTask.user_id == user_id,
            MicroTask.status == "completed",
            MicroTask.task_date >= week_start,
            MicroTask.task_date <= week_end,
        )
    )
    week_count = week_result.scalar() or 0

    return {
        "streak": streak,
        "week_completed": week_count,
        "week_start": week_start,
        "week_end": week_end,
    }
