"""一步(StepOne) · 参考案例库 API · V3.0"""
from fastapi import APIRouter
from services.reference_cases import REFERENCE_CASES, get_cases_by_tag

router = APIRouter(prefix="/api/cases", tags=["参考案例"])


@router.get("/list")
async def list_cases(tag: str = ""):
    """获取参考案例列表"""
    cases = get_cases_by_tag(tag)
    return {
        "total": len(cases),
        "cases": cases,
        "disclaimer": "📌 这些只是'路标'，不是'导航'。每个人的路都不同，你的故事由你自己书写。",
    }


@router.get("/detail/{case_id}")
async def get_case_detail(case_id: int):
    """获取单个案例详情"""
    for case in REFERENCE_CASES:
        if case["id"] == case_id:
            return case
    return {"error": "案例不存在"}
