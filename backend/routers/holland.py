"""一步(StepOne) · 霍兰德测评 API · V3.3"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import User, RadarChart, Memory
from services.holland_service import (
    get_questions, calculate_holland, generate_initial_radar,
    HOLLAND_TYPES, HOLLAND_ROLE_MAP,
)

router = APIRouter(prefix="/api/holland", tags=["霍兰德测评"])


class HollandSubmitRequest(BaseModel):
    user_id: int
    answers: list[dict]


@router.get("/questions")
async def questions():
    """获取霍兰德12题精简版"""
    return {"questions": get_questions(), "total": len(get_questions())}


@router.get("/types")
async def types():
    """获取霍兰德六型说明"""
    return {"types": [{"type": k, **v} for k, v in HOLLAND_TYPES.items()]}


@router.post("/submit")
async def submit(req: HollandSubmitRequest, db: AsyncSession = Depends(get_db)):
    """提交霍兰德测评答案"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if len(req.answers) < 6:
        raise HTTPException(status_code=400, detail="请完成至少6道题目")

    # 计算霍兰德结果
    holland_result = calculate_holland(req.answers)

    # 生成初始雷达图
    radar_data = generate_initial_radar(holland_result)

    # 保存雷达图
    chart = RadarChart(
        user_id=req.user_id,
        version=1,
        dimensions=radar_data.get("framework_layer", []),
        interpretation=radar_data.get("interpretation", ""),
        matched_roles=radar_data.get("matched_roles", []),
        generated_from="holland",
    )
    db.add(chart)

    # 创建记忆
    top = holland_result.get("top_types", [])
    top_str = " + ".join([f"{t['name']}({t['type']})" for t in top])
    db.add(Memory(
        user_id=req.user_id,
        memory_type="holland",
        content=f"霍兰德测评结果：{top_str}",
        importance=5,
    ))

    # 初始化对话深度（重置为第1层：建立连接）
    from models import ConversationPhase
    phase_result = await db.execute(
        select(ConversationPhase).where(ConversationPhase.user_id == req.user_id)
    )
    phase = phase_result.scalar_one_or_none()
    if not phase:
        phase = ConversationPhase(user_id=req.user_id, current_phase="depth1")
        db.add(phase)
    else:
        phase.current_phase = "depth1"
        phase.interest_clues = []
        phase.explore_directions = []

    await db.commit()

    return {
        "success": True,
        "holland_result": holland_result,
        "radar_chart_id": chart.id,
        "message": "测评完成！这只是起点，接下来我们聊聊——这是真的你吗？",
    }


@router.get("/result/{user_id}")
async def get_result(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户的霍兰德测评结果"""
    # 从记忆中查找
    result = await db.execute(
        select(Memory).where(
            Memory.user_id == user_id,
            Memory.memory_type == "holland",
        ).order_by(Memory.created_at.desc()).limit(1)
    )
    mem = result.scalar_one_or_none()
    if not mem:
        return {"status": "not_found", "message": "尚未完成霍兰德测评"}

    # 从雷达图中查找
    chart_result = await db.execute(
        select(RadarChart).where(
            RadarChart.user_id == user_id,
            RadarChart.generated_from == "holland",
        ).order_by(RadarChart.created_at.desc()).limit(1)
    )
    chart = chart_result.scalar_one_or_none()

    return {
        "has_result": True,
        "memory": mem.content,
        "radar_chart_id": chart.id if chart else None,
        "dimensions": chart.dimensions if chart else [],
        "matched_roles": chart.matched_roles if chart else [],
    }
