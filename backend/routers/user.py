"""用户 & 引导问卷 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import get_db
from models import User, OnboardingAnswer, StageLog
from services.stage_engine import detect_stage, get_stage_info, get_onboarding_questions, get_grade_options
from data_definitions import STAGES, MAJOR_CATEGORIES, EDUCATION_LEVELS, STAGE_CONTENT_TEMPLATES, INDUSTRIES

router = APIRouter(prefix="/api/user", tags=["用户"])


# ---------- Pydantic Schemas ----------
class UserLoginRequest(BaseModel):
    openid: str
    nickname: str = ""
    avatar_url: str = ""


class OnboardingSubmitRequest(BaseModel):
    user_id: int
    major_category: str
    education_type: str
    grade: str
    major_name: str = ""
    target_industries: list[str] = []
    graduation_year: Optional[int] = None
    has_internship: bool = False
    has_offer: bool = False
    is_preparing_exam: bool = False
    manually_selected_stage: Optional[str] = None


class StageUpdateRequest(BaseModel):
    user_id: int
    new_stage: str
    reason: str = ""


# ---------- API Routes ----------

@router.post("/login")
async def user_login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录/注册"""
    result = await db.execute(select(User).where(User.openid == req.openid))
    user = result.scalar_one_or_none()

    if user:
        user.nickname = req.nickname or user.nickname
        user.avatar_url = req.avatar_url or user.avatar_url
        user.updated_at = datetime.utcnow()
    else:
        user = User(
            openid=req.openid,
            nickname=req.nickname,
            avatar_url=req.avatar_url,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "onboarding_completed": user.onboarding_completed,
        "current_stage": user.current_stage,
        "profile": {
            "major_category": user.major_category,
            "major_name": user.major_name,
            "education_type": user.education_type,
            "grade": user.grade,
            "target_industries": user.target_industries,
        }
    }


@router.get("/onboarding/questions")
async def get_questions(education_type: str = ""):
    """获取引导问卷题目"""
    questions = get_onboarding_questions()

    # 如果已选择学历类型，则动态返回年级选项
    if education_type:
        grade_opts = get_grade_options(education_type)
        questions.append({
            "key": "grade",
            "title": "你目前是哪个年级/阶段？",
            "type": "single_choice",
            "options": grade_opts,
        })

    return {"questions": questions, "total": len(questions)}


@router.get("/onboarding/grade-options")
async def grade_options(education_type: str):
    """根据学历类型获取年级选项"""
    return {"options": get_grade_options(education_type)}


@router.post("/onboarding/submit")
async def submit_onboarding(req: OnboardingSubmitRequest, db: AsyncSession = Depends(get_db)):
    """提交引导问卷，完成用户画像定位"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 阶段识别
    detected_stage = detect_stage(
        education_type=req.education_type,
        grade=req.grade,
        has_internship=req.has_internship,
        has_offer=req.has_offer,
        is_preparing_exam=req.is_preparing_exam,
        manually_selected=req.manually_selected_stage,
    )

    old_stage = user.current_stage

    # 更新用户画像
    user.major_category = req.major_category
    user.major_name = req.major_name
    user.education_type = req.education_type
    user.grade = req.grade
    user.current_stage = detected_stage
    user.target_industries = req.target_industries
    user.graduation_year = req.graduation_year
    user.onboarding_completed = 1
    user.updated_at = datetime.utcnow()

    # 记录阶段变更
    if old_stage != detected_stage:
        db.add(StageLog(
            user_id=user.id,
            from_stage=old_stage,
            to_stage=detected_stage,
            reason="引导问卷完成，自动识别阶段",
        ))

    await db.commit()
    await db.refresh(user)

    stage_info = get_stage_info(detected_stage)

    return {
        "success": True,
        "current_stage": detected_stage,
        "stage_info": {
            "id": stage_info["id"],
            "name": stage_info["name"],
            "emoji": stage_info["emoji"],
            "description": stage_info["description"],
            "core_needs": stage_info["core_needs"],
            "key_actions": stage_info["key_actions"],
        },
        "welcome_message": _generate_welcome_message(
            stage_info, user.nickname, req.major_category
        ),
        "profile": {
            "major_category": user.major_category,
            "major_name": user.major_name,
            "education_type": user.education_type,
            "grade": user.grade,
            "target_industries": user.target_industries,
            "graduation_year": user.graduation_year,
        }
    }


@router.get("/profile/{user_id}")
async def get_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户完整画像"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    stage_info = get_stage_info(user.current_stage)
    major_cat = MAJOR_CATEGORIES.get(user.major_category, {})
    edu_info = EDUCATION_LEVELS.get(user.education_type, {})
    grade_info = edu_info.get("grades", {}).get(user.grade, {}) if edu_info else {}

    return {
        "id": user.id,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "onboarding_completed": user.onboarding_completed,
        "current_stage": user.current_stage,
        "stage_emoji": stage_info.get("emoji", ""),
        "stage_name": stage_info.get("name", ""),
        "profile": {
            "major_category": user.major_category,
            "major_category_name": major_cat.get("name", ""),
            "major_name": user.major_name,
            "education_type": user.education_type,
            "education_type_name": edu_info.get("name", ""),
            "grade": user.grade,
            "grade_name": grade_info.get("name", ""),
            "target_industries": user.target_industries,
            "graduation_year": user.graduation_year,
            "career_directions": major_cat.get("career_directions", []),
            "grade_stage": grade_info.get("stage", ""),
            "grade_key_months": grade_info.get("key_months", ""),
        },
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


@router.post("/stage")
async def update_stage(req: StageUpdateRequest, db: AsyncSession = Depends(get_db)):
    """手动更新用户阶段"""
    if req.new_stage not in STAGES:
        raise HTTPException(status_code=400, detail="无效的阶段")

    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    old_stage = user.current_stage
    user.current_stage = req.new_stage
    user.updated_at = datetime.utcnow()

    if old_stage != req.new_stage:
        db.add(StageLog(
            user_id=user.id,
            from_stage=old_stage,
            to_stage=req.new_stage,
            reason=req.reason or "用户手动更新",
        ))

    await db.commit()

    stage_info = get_stage_info(req.new_stage)
    return {
        "success": True,
        "current_stage": req.new_stage,
        "stage_info": {
            "id": stage_info["id"],
            "name": stage_info["name"],
            "emoji": stage_info["emoji"],
            "description": stage_info["description"],
        }
    }


@router.get("/stages")
async def list_stages():
    """获取所有阶段列表（用于阶段选择器）"""
    return {
        "stages": [
            {"id": k, "name": v["name"], "emoji": v["emoji"], "description": v["description"]}
            for k, v in STAGES.items()
        ]
    }


@router.get("/industries")
async def list_industries():
    """获取行业列表"""
    return {"industries": INDUSTRIES}


def _generate_welcome_message(stage_info: dict, nickname: str, major_category: str) -> str:
    """生成阶段欢迎语"""
    major_cat = MAJOR_CATEGORIES.get(major_category, {})
    major_name = major_cat.get("name", "")
    name = nickname or "同学"

    welcome_templates = {
        "S1": f"Hi {name}！👋 欢迎来到一步。你现在正处于大学最宝贵的探索期，很多人和你一样对专业和未来感到迷茫，这完全正常！{major_name}专业的出路比你想象的丰富得多，我们一步一步来了解。先从探索你的兴趣开始吧？",
        "S2": f"Hi {name}！📚 你已经进入了专业积累的关键阶段。{major_name}专业的核心竞争力是什么？不同方向需要什么技能？我可以帮你做一次能力差距分析，制定接下来半年的学习计划。",
        "S3": f"Hi {name}！📝 实习准备期到了，这是拿到大厂Offer最关键的一步。{major_name}专业对口的岗位有哪些？你的简历目前最大的问题是什么？我们可以一起拆解JD、打磨简历、模拟面试。",
        "S4": f"Hi {name}！💼 正在实习中，这是验证职业方向最好的机会。今天实习有什么感受？遇到了什么困惑？我们可以一起复盘，帮你判断「这个方向到底适不适合我」。",
        "S5": f"Hi {name}！🎯 正式求职期，我知道这段时间压力很大。但你已经准备好了！我们可以一起管理投递节奏、复盘面试、比较Offer。记住，秋招/春招是一场马拉松，不是短跑。",
        "S6": f"Hi {name}！🎉 恭喜拿到Offer！这段时间容易出现「空窗焦虑」——不知道该做什么。别担心，我帮你规划入职前的准备：了解公司文化、预习技能、调整心态，让你从容开启职场。",
        "S7": f"Hi {name}！🎓 深造准备期，考研/保研/留学是一条需要全力以赴的路。但我也会提醒你做好Plan B——如果申请失利，求职该怎么走。两条腿走路，心态会更稳。",
    }
    return welcome_templates.get(stage_info["id"], welcome_templates["S1"])
