"""成长路线图 & 里程碑服务"""
from datetime import datetime, timedelta
from data_definitions import ROADMAP_TEMPLATES


def generate_roadmap(target_role: str = "", template_key: str = "general") -> dict:
    """为用户生成成长路线图"""
    template = ROADMAP_TEMPLATES.get(template_key, ROADMAP_TEMPLATES["general"])

    stages = []
    total_milestones = 0
    total_hours = 0

    for i, stage_template in enumerate(template["stages"]):
        milestones = []
        for j, ms in enumerate(stage_template["milestones"]):
            total_milestones += 1
            total_hours += ms["hours"]
            milestones.append({
                "name": ms["name"],
                "verification": ms["verification"],
                "estimated_hours": ms["hours"],
                "status": "pending",
                "sort_order": j,
            })

        stages.append({
            "name": stage_template["name"],
            "icon": stage_template["icon"],
            "sort_order": i,
            "progress": 0.0,
            "status": "pending" if i > 0 else "in_progress",
            "milestones": milestones,
            "milestone_count": len(milestones),
            "completed_count": 0,
        })

    return {
        "template_key": template_key,
        "target_role": target_role or template["name"],
        "total_progress": 0.0,
        "total_milestones": total_milestones,
        "total_hours": total_hours,
        "stages": stages,
    }


def get_template_list() -> list:
    """获取可用的路线图模板列表"""
    return [
        {"key": k, "name": v["name"], "stages_count": len(v["stages"])}
        for k, v in ROADMAP_TEMPLATES.items()
    ]


def get_week_range() -> tuple:
    """获取本周起止日期"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


def get_suggested_role(major_category: str) -> str:
    """根据专业大类推荐适合的岗位"""
    suggestions = {
        "science": "数据分析师",
        "engineering": "后端开发工程师",
        "arts": "内容运营",
        "social_science": "人力资源",
        "business": "行业分析师",
        "medicine": "医药研发",
        "agriculture_other": "通用岗位",
    }
    return suggestions.get(major_category, "通用岗位")
