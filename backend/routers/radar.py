"""一步(StepOne) · 人才雷达图 API · V3.3 双图层"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import User, RadarChart, Conversation, Memory, UserMilestone, StoryMaterial
from services.radar_service import (
    extract_traits_from_messages, generate_radar_with_ai,
    get_role_matches, _fallback_radar, merge_radar_layers,
)

router = APIRouter(prefix="/api/radar", tags=["人才雷达图"])


class GenerateRadarRequest(BaseModel):
    user_id: int


@router.post("/generate")
async def generate_radar(req: GenerateRadarRequest, db: AsyncSession = Depends(get_db)):
    """生成人才雷达图"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 收集对话数据
    conv_result = await db.execute(
        select(Conversation).where(Conversation.user_id == req.user_id, Conversation.role == "user")
        .order_by(desc(Conversation.created_at)).limit(20)
    )
    messages = [c.content for c in conv_result.scalars().all()]

    if len(messages) < 3:
        return {
            "status": "insufficient_data",
            "message": "还需要更多对话才能生成雷达图，继续聊聊吧",
            "dimensions": [],
        }

    # 获取里程碑和故事素材
    ms_result = await db.execute(
        select(UserMilestone).where(UserMilestone.user_id == req.user_id)
    )
    milestones = [{"name": m.name, "status": m.status} for m in ms_result.scalars().all()]

    story_result = await db.execute(
        select(StoryMaterial).where(StoryMaterial.user_id == req.user_id)
    )
    stories = [{"title": s.title, "trait_revealed": s.trait_revealed} for s in story_result.scalars().all()]

    # 获取霍兰德框架层
    holland_result = await db.execute(
        select(RadarChart).where(
            RadarChart.user_id == req.user_id,
            RadarChart.generated_from == "holland",
        ).order_by(desc(RadarChart.id)).limit(1)
    )
    holland_chart = holland_result.scalar_one_or_none()
    framework_layer = holland_chart.dimensions if holland_chart else []

    # 生成对话特质层
    dialogue_radar = await generate_radar_with_ai(messages, milestones, stories)
    dialogue_layer = dialogue_radar.get("dialogue_layer", dialogue_radar.get("dimensions", []))

    # 双图层合并
    radar_data = merge_radar_layers(
        framework_layer,
        dialogue_layer,
        holland_chart.matched_roles if holland_chart else None,
    )

    # 版本号
    version = 1
    old_result = await db.execute(
        select(RadarChart).where(RadarChart.user_id == req.user_id).order_by(desc(RadarChart.id)).limit(1)
    )
    old = old_result.scalar_one_or_none()
    if old:
        version = old.version + 1

    matched = radar_data.get("matched_roles", []) or get_role_matches(dialogue_layer)

    chart = RadarChart(
        user_id=req.user_id,
        version=version,
        dimensions=radar_data.get("dimensions", []),
        interpretation=radar_data.get("interpretation", ""),
        matched_roles=matched,
        generated_from="dialog",
    )
    db.add(chart)

    # 记忆
    db.add(Memory(
        user_id=req.user_id,
        memory_type="radar",
        content=f"雷达图V{version}：{', '.join([d.get('name','') for d in radar_data.get('dimensions',[])])}",
        importance=4,
    ))

    await db.commit()
    await db.refresh(chart)

    return {
        "id": chart.id,
        "version": version,
        "dimensions": radar_data.get("dimensions", []),
        "interpretation": radar_data.get("interpretation", ""),
        "disclaimer": radar_data.get("disclaimer", "这只是基于目前对话的初步观察"),
        "matched_roles": matched,
        "created_at": chart.created_at.isoformat() if chart.created_at else None,
    }


@router.get("/view/{user_id}")
async def view_radar(user_id: int, version: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """查看雷达图"""
    query = select(RadarChart).where(RadarChart.user_id == user_id)
    if version:
        query = query.where(RadarChart.version == version)
    query = query.order_by(desc(RadarChart.created_at)).limit(1)

    result = await db.execute(query)
    chart = result.scalar_one_or_none()

    if not chart:
        return {"status": "not_found", "message": "尚未生成雷达图，请先进行对话"}

    return {
        "id": chart.id,
        "version": chart.version,
        "dimensions": chart.dimensions,
        "interpretation": chart.interpretation,
        "matched_roles": chart.matched_roles,
        "created_at": chart.created_at.isoformat() if chart.created_at else None,
    }


@router.get("/history/{user_id}")
async def radar_history(user_id: int, db: AsyncSession = Depends(get_db)):
    """查看雷达图历史版本"""
    result = await db.execute(
        select(RadarChart).where(RadarChart.user_id == user_id)
        .order_by(desc(RadarChart.created_at)).limit(10)
    )
    charts = result.scalars().all()
    return {
        "versions": [
            {
                "id": c.id,
                "version": c.version,
                "dimension_count": len(c.dimensions),
                "interpretation": c.interpretation[:100],
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in charts
        ],
        "total": len(charts),
    }
