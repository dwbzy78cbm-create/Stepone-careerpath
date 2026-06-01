"""一步(StepOne) · 成长记忆胶囊 API · V3.0"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from database import get_db
from models import User, Memory, StoryMaterial, UserMilestone
from services.memory_service import generate_memory_summary

router = APIRouter(prefix="/api/memory", tags=["记忆胶囊"])


class SaveMemoryRequest(BaseModel):
    user_id: int
    memory_type: str
    content: str
    keywords: list = []
    importance: int = 1


@router.post("/save")
async def save_memory(req: SaveMemoryRequest, db: AsyncSession = Depends(get_db)):
    """保存一条记忆"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="用户不存在")

    memory = Memory(
        user_id=req.user_id,
        memory_type=req.memory_type,
        content=req.content,
        keywords=req.keywords,
        importance=req.importance,
    )
    db.add(memory)
    await db.commit()
    return {"success": True, "id": memory.id}


@router.get("/summary/{user_id}")
async def get_memory_summary(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户记忆胶囊摘要"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取所有记忆
    mem_result = await db.execute(
        select(Memory).where(Memory.user_id == user_id)
        .order_by(desc(Memory.created_at)).limit(50)
    )
    memories = [{
        "memory_type": m.memory_type, "content": m.content,
        "importance": m.importance, "created_at": m.created_at.isoformat() if m.created_at else None,
    } for m in mem_result.scalars().all()]

    # 获取里程碑
    ms_result = await db.execute(
        select(UserMilestone).where(UserMilestone.user_id == user_id)
    )
    milestones = [{"name": m.name, "status": m.status, "reflection": m.reflection}
                  for m in ms_result.scalars().all()]

    # 获取故事素材
    story_result = await db.execute(
        select(StoryMaterial).where(StoryMaterial.user_id == user_id)
    )
    stories = [{"title": s.title, "trait_revealed": s.trait_revealed, "status": s.status}
               for s in story_result.scalars().all()]

    summary = generate_memory_summary(user_id, memories, [], user.current_stage, milestones, stories)

    return {
        "user_stage": user.current_stage,
        "anxiety_level": user.anxiety_level,
        "silent_mode": bool(user.silent_mode),
        "summary": summary,
        "recent_memories": memories[:5],
    }


@router.get("/list/{user_id}")
async def list_memories(user_id: int, memory_type: str = "", limit: int = 20, db: AsyncSession = Depends(get_db)):
    """获取记忆列表"""
    query = select(Memory).where(Memory.user_id == user_id)
    if memory_type:
        query = query.where(Memory.memory_type == memory_type)
    query = query.order_by(desc(Memory.created_at)).limit(limit)

    result = await db.execute(query)
    return {
        "memories": [{
            "id": m.id, "memory_type": m.memory_type, "content": m.content,
            "importance": m.importance, "created_at": m.created_at.isoformat() if m.created_at else None,
        } for m in result.scalars().all()]
    }


# ============ V3.0 故事素材 API ============

class SaveStoryRequest(BaseModel):
    user_id: int
    title: str = ""
    raw_experience: str = ""
    key_moment: str = ""
    inner_thought: str = ""
    trait_revealed: str = ""


@router.post("/story/save")
async def save_story(req: SaveStoryRequest, db: AsyncSession = Depends(get_db)):
    """保存故事素材"""
    story = StoryMaterial(
        user_id=req.user_id,
        title=req.title,
        raw_experience=req.raw_experience,
        key_moment=req.key_moment,
        inner_thought=req.inner_thought,
        trait_revealed=req.trait_revealed,
    )
    db.add(story)
    await db.commit()
    await db.refresh(story)

    # 同时创建记忆
    db.add(Memory(
        user_id=req.user_id,
        memory_type="story_clue",
        content=f"故事素材：{req.title} - {req.trait_revealed}",
        importance=4,
    ))
    await db.commit()

    return {"success": True, "id": story.id, "title": story.title}


@router.get("/story/list/{user_id}")
async def list_stories(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取所有故事素材"""
    result = await db.execute(
        select(StoryMaterial).where(StoryMaterial.user_id == user_id)
        .order_by(desc(StoryMaterial.updated_at))
    )
    return {
        "stories": [{
            "id": s.id, "title": s.title,
            "raw_experience": s.raw_experience[:200],
            "key_moment": s.key_moment,
            "inner_thought": s.inner_thought,
            "trait_revealed": s.trait_revealed,
            "reconstructed_story": s.reconstructed_story,
            "status": s.status,
        } for s in result.scalars().all()]
    }
