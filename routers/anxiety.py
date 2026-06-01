"""一步(StepOne) · 焦虑急救包 + 留白机制 API · V3.0"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timedelta

from database import get_db
from models import User, AnxietyLog
from services.anxiety_service import (
    get_anxiety_flow, detect_emotion_type,
    should_suggest_break, get_silent_mode_message,
)

router = APIRouter(prefix="/api/anxiety", tags=["焦虑急救+留白"])


class AnxietyTriggerRequest(BaseModel):
    user_id: int
    text: str
    trigger_type: str = "active"


class SilentModeRequest(BaseModel):
    user_id: int
    action: str  # enter / exit


@router.post("/trigger")
async def trigger_anxiety_kit(req: AnxietyTriggerRequest, db: AsyncSession = Depends(get_db)):
    """触发焦虑急救包"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    emotion_type = detect_emotion_type(req.text)
    flow = get_anxiety_flow(emotion_type, req.text)

    log = AnxietyLog(
        user_id=req.user_id,
        trigger_type=req.trigger_type,
        emotion_type=emotion_type,
        user_input=req.text,
        ai_response=flow["step2"]["content"],
        micro_action=flow["step3"]["micro_action"],
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)

    return {"log_id": log.id, "emotion_type": emotion_type, "flow": flow}


@router.post("/complete-action")
async def complete_action(req: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AnxietyLog).where(AnxietyLog.id == req.get("log_id", 0)))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="记录不存在")
    log.completed_action = 1
    await db.commit()
    return {"success": True}


# ============ V3.0 静默模式 ============

@router.post("/silent-mode")
async def silent_mode(req: SilentModeRequest, db: AsyncSession = Depends(get_db)):
    """进入/退出静默模式"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if req.action == "enter":
        user.silent_mode = 1
        user.silent_until = datetime.utcnow() + timedelta(days=7)
        await db.commit()
        return {"success": True, "message": get_silent_mode_message(), "silent_until": user.silent_until.isoformat()}

    elif req.action == "exit":
        user.silent_mode = 0
        user.silent_until = None
        await db.commit()
        return {"success": True, "message": "欢迎回来。你准备好继续了吗？不着急，慢慢来。"}

    raise HTTPException(status_code=400, detail="无效的action")


@router.get("/status/{user_id}")
async def get_silent_status(user_id: int, db: AsyncSession = Depends(get_db)):
    """查询静默模式状态"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {
        "silent_mode": bool(user.silent_mode),
        "silent_until": user.silent_until.isoformat() if user.silent_until else None,
        "anxiety_level": user.anxiety_level,
    }


@router.post("/update-anxiety")
async def update_anxiety(req: dict, db: AsyncSession = Depends(get_db)):
    """更新焦虑等级"""
    result = await db.execute(select(User).where(User.id == req.get("user_id", 0)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.anxiety_level = req.get("level", 0)
    await db.commit()
    return {"success": True}


@router.get("/history/{user_id}")
async def get_history(user_id: int, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AnxietyLog).where(AnxietyLog.user_id == user_id)
        .order_by(AnxietyLog.created_at.desc()).limit(limit)
    )
    return {"logs": [{
        "id": l.id, "emotion_type": l.emotion_type,
        "user_input": l.user_input[:100],
        "micro_action": l.micro_action,
        "completed": l.completed_action,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    } for l in result.scalars().all()]}
