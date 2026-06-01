"""对话深度管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import get_db
from models import User, Conversation
from services.conversation_depth import (
    DEPTH_DEFINITIONS,
    DEPTH_TRANSITIONS,
    NARRATIVE_ENTRY_CONDITIONS,
)

router = APIRouter(prefix="/api/depth", tags=["对话深度"])


class DepthUpdateRequest(BaseModel):
    user_id: int
    depth: str
    clues: Optional[list[str]] = None
    fragments: Optional[list[str]] = None


@router.get("/current/{user_id}")
async def get_current_depth(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户当前的对话深度"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取对话消息数量
    msg_result = await db.execute(
        select(Conversation).where(Conversation.user_id == user_id)
    )
    messages = msg_result.scalars().all()
    user_messages = [m for m in messages if m.role == "user"]
    total_messages = len(messages)

    # 计算当前深度
    current_depth = "depth1"
    for depth_id in ["depth1", "depth2", "depth3", "depth4", "depth5"]:
        if depth_id in DEPTH_TRANSITIONS:
            rule = DEPTH_TRANSITIONS[depth_id]
            if total_messages >= rule["min_messages"] and len(user_messages) >= rule["min_user_messages"]:
                current_depth = rule["to"]

    depth_info = DEPTH_DEFINITIONS.get(current_depth, DEPTH_DEFINITIONS["depth1"])

    # 判断是否显示叙事入口
    show_narrative = False
    conditions = NARRATIVE_ENTRY_CONDITIONS
    depth_order = ["depth1", "depth2", "depth3", "depth4", "depth5"]
    current_idx = depth_order.index(current_depth) if current_depth in depth_order else 0
    required_idx = depth_order.index(conditions["min_depth"]) if conditions["min_depth"] in depth_order else 2
    if current_idx >= required_idx and len(user_messages) >= conditions["min_user_messages"]:
        show_narrative = True

    return {
        "current_depth": current_depth,
        "depth_info": depth_info,
        "total_messages": total_messages,
        "user_messages": len(user_messages),
        "show_narrative": show_narrative,
        "all_depths": [
            {
                "id": d["id"],
                "name": d["name"],
                "description": d["description"],
            }
            for d in DEPTH_DEFINITIONS.values()
        ],
    }


@router.post("/update")
async def update_depth(req: DepthUpdateRequest, db: AsyncSession = Depends(get_db)):
    """手动更新对话深度"""
    if req.depth not in DEPTH_DEFINITIONS:
        raise HTTPException(status_code=400, detail="无效的深度级别")

    # 保存到用户的元数据（使用 StageLog 记录）
    from models import StageLog
    db.add(StageLog(
        user_id=req.user_id,
        from_stage="",
        to_stage=req.depth,
        reason=f"AI自动评估: 对话深度更新为 {DEPTH_DEFINITIONS[req.depth]['name']}"
        + (f", 线索: {', '.join(req.clues[:3])}" if req.clues else ""),
    ))
    await db.commit()

    return {
        "success": True,
        "depth": req.depth,
        "depth_name": DEPTH_DEFINITIONS[req.depth]["name"],
    }


@router.get("/check/{user_id}")
async def check_narrative_entry(user_id: int, db: AsyncSession = Depends(get_db)):
    """检查是否应显示叙事入口"""
    depth_data = await get_current_depth(user_id, db)
    return {
        "show_narrative": depth_data["show_narrative"],
        "current_depth": depth_data["current_depth"],
        "depth_name": depth_data["depth_info"]["name"],
        "user_messages": depth_data["user_messages"],
    }


@router.get("/list")
async def list_depths():
    """列出所有对话深度定义"""
    return {
        "depths": [
            {
                "id": d["id"],
                "name": d["name"],
                "description": d["description"],
                "goal": d["goal"],
            }
            for d in DEPTH_DEFINITIONS.values()
        ]
    }
