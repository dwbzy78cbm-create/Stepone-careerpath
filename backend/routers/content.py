"""内容推荐 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from database import get_db
from models import User, ContentItem
from data_definitions import STAGE_CONTENT_TEMPLATES, STAGES

router = APIRouter(prefix="/api/content", tags=["内容推荐"])


@router.get("/stage/{user_id}")
async def get_stage_content(user_id: int, db: AsyncSession = Depends(get_db)):
    """根据用户阶段获取推荐内容"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    stage_id = user.current_stage
    template = STAGE_CONTENT_TEMPLATES.get(stage_id, STAGE_CONTENT_TEMPLATES["S1"])
    stage_info = STAGES.get(stage_id, STAGES["S1"])

    # 从数据库获取该阶段的内容
    db_result = await db.execute(
        select(ContentItem)
        .where(
            ContentItem.is_active == 1,
            ContentItem.stage_tag == stage_id,
        )
        .order_by(ContentItem.sort_order)
        .limit(20)
    )
    db_items = db_result.scalars().all()

    # 合并模板和数据库内容
    sections = []
    for section in template["sections"]:
        section_data = {
            "type": section["type"],
            "title": section["title"],
            "desc": section["desc"],
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "type": item.type,
                    "content": item.content[:200] if item.content else "",
                    "url": item.url,
                }
                for item in db_items if item.type == section["type"]
            ],
        }
        sections.append(section_data)

    return {
        "stage": {
            "id": stage_id,
            "name": stage_info["name"],
            "emoji": stage_info["emoji"],
        },
        "title": template["title"],
        "sections": sections,
    }


@router.get("/item/{item_id}")
async def get_content_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """获取单条内容详情"""
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == item_id, ContentItem.is_active == 1)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="内容不存在")

    return {
        "id": item.id,
        "title": item.title,
        "type": item.type,
        "content": item.content,
        "url": item.url,
        "stage_tag": item.stage_tag,
        "industry_tag": item.industry_tag,
        "major_tag": item.major_tag,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }
