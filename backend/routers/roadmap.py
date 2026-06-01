"""成长路线图 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from database import get_db
from models import User, Roadmap, RoadmapStage, Milestone, WeeklySummary
from services.roadmap_service import generate_roadmap, get_template_list, get_week_range, get_suggested_role

router = APIRouter(prefix="/api/roadmap", tags=["成长路线图"])


class CreateRoadmapRequest(BaseModel):
    user_id: int
    template_key: str = "general"
    target_role: str = ""


class UpdateMilestoneRequest(BaseModel):
    user_id: int
    milestone_id: int
    status: str


@router.post("/create")
async def create_roadmap(req: CreateRoadmapRequest, db: AsyncSession = Depends(get_db)):
    """为用户创建成长路线图"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 如果已有路线图，先删除
    exist_result = await db.execute(select(Roadmap).where(Roadmap.user_id == req.user_id))
    existing = exist_result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.commit()

    template_data = generate_roadmap(req.target_role or get_suggested_role(user.major_category), req.template_key)

    roadmap = Roadmap(
        user_id=req.user_id,
        template_key=template_data["template_key"],
        target_role=template_data["target_role"],
        total_progress=0.0,
    )
    db.add(roadmap)
    await db.flush()

    for stage_data in template_data["stages"]:
        stage = RoadmapStage(
            roadmap_id=roadmap.id,
            name=stage_data["name"],
            icon=stage_data["icon"],
            sort_order=stage_data["sort_order"],
            progress=0.0,
            status=stage_data["status"],
        )
        db.add(stage)
        await db.flush()

        for ms_data in stage_data["milestones"]:
            milestone = Milestone(
                stage_id=stage.id,
                name=ms_data["name"],
                verification=ms_data["verification"],
                estimated_hours=ms_data["estimated_hours"],
                status="pending",
            )
            db.add(milestone)

    user.target_role = req.target_role or template_data["target_role"]
    await db.commit()

    return {"success": True, "roadmap_id": roadmap.id, "target_role": template_data["target_role"]}


@router.get("/view/{user_id}")
async def view_roadmap(user_id: int, db: AsyncSession = Depends(get_db)):
    """查看用户的成长路线图"""
    result = await db.execute(select(Roadmap).where(Roadmap.user_id == user_id))
    roadmap = result.scalar_one_or_none()
    if not roadmap:
        return {"has_roadmap": False, "message": "尚未创建路线图，请先完成规划"}

    stages_result = await db.execute(
        select(RoadmapStage).where(RoadmapStage.roadmap_id == roadmap.id).order_by(RoadmapStage.sort_order)
    )
    stages = stages_result.scalars().all()

    stages_data = []
    for stage in stages:
        ms_result = await db.execute(
            select(Milestone).where(Milestone.stage_id == stage.id).order_by(Milestone.id)
        )
        milestones = ms_result.scalars().all()
        ms_data = [
            {
                "id": m.id,
                "name": m.name,
                "verification": m.verification,
                "estimated_hours": m.estimated_hours,
                "status": m.status,
                "completed_at": m.completed_at.isoformat() if m.completed_at else None,
            }
            for m in milestones
        ]
        completed = sum(1 for m in milestones if m.status == "completed")
        stages_data.append({
            "id": stage.id,
            "name": stage.name,
            "icon": stage.icon,
            "sort_order": stage.sort_order,
            "progress": stage.progress,
            "status": stage.status,
            "milestones": ms_data,
            "milestone_count": len(milestones),
            "completed_count": completed,
        })

    return {
        "has_roadmap": True,
        "id": roadmap.id,
        "target_role": roadmap.target_role,
        "template_key": roadmap.template_key,
        "total_progress": roadmap.total_progress,
        "stages": stages_data,
    }


@router.post("/milestone/update")
async def update_milestone(req: UpdateMilestoneRequest, db: AsyncSession = Depends(get_db)):
    """更新里程碑状态"""
    result = await db.execute(select(Milestone).where(Milestone.id == req.milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="里程碑不存在")

    old_status = milestone.status
    milestone.status = req.status
    if req.status == "completed":
        milestone.completed_at = datetime.utcnow()

    await db.flush()

    # 更新阶段进度
    stage_result = await db.execute(select(RoadmapStage).where(RoadmapStage.id == milestone.stage_id))
    stage = stage_result.scalar_one_or_none()
    if stage:
        ms_result = await db.execute(select(Milestone).where(Milestone.stage_id == stage.id))
        all_ms = ms_result.scalars().all()
        completed = sum(1 for m in all_ms if m.status == "completed")
        stage.progress = round(completed / len(all_ms) * 100, 1) if all_ms else 0
        stage.status = "completed" if stage.progress >= 100 else "in_progress"

        # 更新总进度
        road_result = await db.execute(select(Roadmap).where(Roadmap.id == stage.roadmap_id))
        road = road_result.scalar_one_or_none()
        if road:
            all_stages_result = await db.execute(
                select(RoadmapStage).where(RoadmapStage.roadmap_id == road.id)
            )
            all_stages = all_stages_result.scalars().all()
            total_ms = 0
            all_completed = 0
            for s in all_stages:
                s_ms_result = await db.execute(select(Milestone).where(Milestone.stage_id == s.id))
                s_ms = s_ms_result.scalars().all()
                total_ms += len(s_ms)
                all_completed += sum(1 for m in s_ms if m.status == "completed")
            road.total_progress = round(all_completed / total_ms * 100, 1) if total_ms else 0

    await db.commit()

    return {
        "success": True,
        "milestone_id": milestone.id,
        "new_status": req.status,
        "stage_progress": stage.progress if stage else 0,
        "total_progress": road.total_progress if 'road' in dir() else 0,
    }


@router.get("/weekly/{user_id}")
async def get_weekly_summary(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取本周成长小结"""
    week_start, week_end = get_week_range()

    result = await db.execute(
        select(WeeklySummary)
        .where(WeeklySummary.user_id == user_id, WeeklySummary.week_start == week_start)
    )
    summary = result.scalar_one_or_none()

    if summary:
        return {
            "week_start": summary.week_start,
            "week_end": summary.week_end,
            "completed_tasks": summary.completed_tasks,
            "total_tasks": summary.total_tasks,
            "milestones_completed": summary.milestones_completed,
            "highlights": summary.highlights,
            "ai_summary": summary.ai_summary,
            "next_week_advice": summary.next_week_advice,
        }
    return {
        "week_start": week_start,
        "week_end": week_end,
        "completed_tasks": 0,
        "total_tasks": 0,
        "milestones_completed": [],
        "message": "本周暂无数据，完成微任务后会自动生成小结",
    }


@router.get("/templates")
async def list_templates():
    """获取可用路线图模板"""
    return {"templates": get_template_list()}


@router.get("/suggested-role/{user_id}")
async def suggest_role(user_id: int, db: AsyncSession = Depends(get_db)):
    """根据用户画像推荐适合的岗位"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"suggested_role": get_suggested_role(user.major_category)}
