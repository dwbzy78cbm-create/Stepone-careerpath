"""一步(StepOne) · 成长记忆胶囊服务 · V3.0"""
from datetime import datetime
from typing import Optional


def generate_memory_summary(
    user_id: int,
    memories: list,
    recent_conversations: list,
    current_stage: str,
    milestones: list,
    story_materials: list,
) -> dict:
    """生成用户的完整记忆摘要"""

    # 按类型整理记忆
    profile_memories = [m for m in memories if m.get("memory_type") == "profile"]
    dialog_memories = [m for m in memories if m.get("memory_type") == "dialog_summary"]
    milestone_memories = [m for m in memories if m.get("memory_type") == "milestone"]
    story_memories = [m for m in memories if m.get("memory_type") == "story_clue"]
    emotion_memories = [m for m in memories if m.get("memory_type") == "emotion"]

    # 对话摘要
    dialog_summary = []
    for m in dialog_memories[-5:]:
        dialog_summary.append(m.get("content", ""))

    # 里程碑进展
    milestone_status = []
    for m in milestones:
        milestone_status.append({
            "name": m.get("name", ""),
            "status": m.get("status", ""),
            "reflection": m.get("reflection", ""),
        })

    # 故事素材
    stories = []
    for s in story_materials:
        stories.append({
            "title": s.get("title", ""),
            "key_moment": s.get("key_moment", ""),
            "trait_revealed": s.get("trait_revealed", ""),
        })

    # 情绪趋势
    recent_emotions = [m.get("content", "") for m in emotion_memories[-3:]]

    return {
        "profile": {
            "total_memories": len(memories),
            "dialog_count": len(dialog_memories),
            "story_count": len(story_memories),
        },
        "recent_dialog_summary": dialog_summary[-1] if dialog_summary else "",
        "key_discoveries": [m.get("content", "") for m in story_memories[-3:]],
        "milestones": milestone_status,
        "stories": stories,
        "recent_emotions": recent_emotions,
        "anxiety_trend": "rising" if len(emotion_memories) >= 3 else "stable",
    }


def should_create_dialog_memory(recent_messages: list) -> bool:
    """判断是否应该从对话中创建记忆"""
    # 当对话轮次超过 6 轮（3 组问答）时，生成一条摘要记忆
    if len(recent_messages) >= 6:
        return True
    return False
