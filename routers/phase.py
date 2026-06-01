"""一步(StepOne) · 对话阶段 API（V3.4 兼容层——委托给 depth 模块）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import ConversationPhase, Memory
from services.conversation_depth import (
    DEPTH_LEVELS, get_depth_opening, detect_branch_type,
    get_branch_response, should_advance_depth,
)

router = APIRouter(prefix="/api/phase", tags=["对话阶段（兼容）"])


class UpdatePhaseRequest(BaseModel):
    user_id: int
    interest_clues: Optional[list] = None
    explore_directions: Optional[list] = None
    concerns: Optional[list] = None
    min_attempt: Optional[str] = None
    pending_questions: Optional[list] = None
    next_goal: Optional[str] = None
    force_phase: Optional[str] = None


class DetectBranchRequest(BaseModel):
    user_id: int
    text: str


@router.get("/current/{user_id}")
async def get_current_phase(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户当前对话深度（兼容旧 API）"""
    result = await db.execute(
        select(ConversationPhase).where(ConversationPhase.user_id == user_id)
    )
    depth_record = result.scalar_one_or_none()

    if not depth_record:
        depth_record = ConversationPhase(user_id=user_id, current_phase="depth1")
        db.add(depth_record)
        await db.commit()
        await db.refresh(depth_record)

    depth_info = DEPTH_LEVELS.get(depth_record.current_phase, DEPTH_LEVELS["depth1"])

    return {
        "current_phase": depth_record.current_phase,
        "phase_name": depth_info["name"],
        "phase_goal": depth_info["goal"],
        "key_questions": depth_info.get("sample_questions", []),
        "output": depth_info.get("output", ""),
        "interest_clues": depth_record.interest_clues,
        "explore_directions": depth_record.explore_directions,
        "concerns": depth_record.concerns,
        "min_attempt": depth_record.min_attempt,
        "pending_questions": depth_record.pending_questions,
        "next_goal": depth_record.next_goal,
        "depth_level": depth_info["depth"],
    }


@router.post("/update")
async def update_phase(req: UpdatePhaseRequest, db: AsyncSession = Depends(get_db)):
    """更新对话深度数据（兼容旧 API）"""
    result = await db.execute(
        select(ConversationPhase).where(ConversationPhase.user_id == req.user_id)
    )
    depth_record = result.scalar_one_or_none()

    if not depth_record:
        depth_record = ConversationPhase(user_id=req.user_id, current_phase="depth1")
        db.add(depth_record)

    if req.interest_clues is not None:
        depth_record.interest_clues = req.interest_clues
    if req.explore_directions is not None:
        depth_record.explore_directions = req.explore_directions
    if req.concerns is not None:
        depth_record.concerns = req.concerns
    if req.min_attempt is not None:
        depth_record.min_attempt = req.min_attempt
    if req.pending_questions is not None:
        depth_record.pending_questions = req.pending_questions
    if req.next_goal is not None:
        depth_record.next_goal = req.next_goal

    # 使用 V3.4 推进逻辑
    fragments = req.explore_directions or depth_record.explore_directions or []
    clues = req.interest_clues or depth_record.interest_clues or []
    confirmed = bool(req.min_attempt or depth_record.min_attempt)

    should_adv, new_depth, reason = should_advance_depth(
        depth_record.current_phase, len(fragments), len(clues), confirmed
    )

    old_depth = depth_record.current_phase
    if should_adv:
        depth_record.current_phase = new_depth

    if req.force_phase and req.force_phase in DEPTH_LEVELS:
        depth_record.current_phase = req.force_phase

    await db.commit()

    if old_depth != depth_record.current_phase:
        db.add(Memory(
            user_id=req.user_id,
            memory_type="depth_change",
            content=f"对话深度从{old_depth}推进到{depth_record.current_phase}",
            importance=3,
        ))
        await db.commit()

    depth_info = DEPTH_LEVELS.get(depth_record.current_phase, DEPTH_LEVELS["depth1"])

    return {
        "current_phase": depth_record.current_phase,
        "phase_name": depth_info["name"],
        "phase_advanced": old_depth != depth_record.current_phase,
        "opening": get_depth_opening(depth_record.current_phase),
    }


@router.post("/detect-branch")
async def detect_branch(req: DetectBranchRequest):
    """检测用户回答类型（兼容旧 API）"""
    branch_type = detect_branch_type(req.text)
    branch_info = get_branch_response(branch_type)
    return {
        "branch_type": branch_type,
        "description": branch_info.get("description", ""),
        "strategy": branch_info.get("strategy", ""),
    }


@router.get("/phases")
async def list_phases():
    """获取五层深度概览（兼容旧 API，字段名保持 phases）"""
    return {
        "phases": [
            {
                "id": k,
                "name": v["name"],
                "depth": v["depth"],
                "goal": v["goal"],
                "key_questions": v.get("sample_questions", []),
                "output": v.get("output", ""),
            }
            for k, v in DEPTH_LEVELS.items()
        ]
    }


@router.get("/opening/{depth_id}")
async def get_opening(depth_id: str):
    """获取指定深度的对话开场白"""
    if depth_id not in DEPTH_LEVELS:
        raise HTTPException(status_code=404, detail=f"未知深度: {depth_id}")
    return {"opening": get_depth_opening(depth_id)}
