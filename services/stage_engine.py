"""阶段识别引擎 —— 根据用户画像自动推荐当前阶段"""
from typing import Optional
from data_definitions import STAGES


def detect_stage(
    education_type: str,
    grade: str,
    has_internship: bool = False,
    has_offer: bool = False,
    is_preparing_exam: bool = False,
    manually_selected: Optional[str] = None,
) -> str:
    """
    根据用户的学历类型、年级和附加信息，自动识别当前阶段。

    优先级：手动选择 > 已拿Offer > 备考 > 实习中 > 学历+年级推断
    """
    # 如果用户手动选择了阶段，直接使用
    if manually_selected and manually_selected in STAGES:
        return manually_selected

    # 已拿到Offer → S6
    if has_offer:
        return "S6"

    # 正在备考/申请 → S7
    if is_preparing_exam:
        return "S7"

    # 正在实习中 → S4
    if has_internship:
        return "S4"

    # 根据学历和年级推断
    grade_stage_map = {
        # 国内本科
        ("domestic_bachelor", "freshman"): "S1",
        ("domestic_bachelor", "sophomore"): "S2",
        ("domestic_bachelor", "junior"): "S3",
        ("domestic_bachelor", "senior"): "S5",
        ("domestic_bachelor", "fifth_year"): "S5",
        # 国内硕士
        ("domestic_master", "year1"): "S2",
        ("domestic_master", "year2"): "S3",
        ("domestic_master", "year3"): "S5",
        # 国内博士
        ("domestic_phd", "year1_2"): "S2",
        ("domestic_phd", "year3_4"): "S3",
        ("domestic_phd", "year5_plus"): "S5",
        # 海外本科
        ("overseas_bachelor", "freshman"): "S1",
        ("overseas_bachelor", "sophomore"): "S2",
        ("overseas_bachelor", "junior"): "S3",
        ("overseas_bachelor", "senior"): "S5",
        # 海外硕士
        ("overseas_master", "one_year"): "S5",
        ("overseas_master", "one_half_year"): "S3",
        ("overseas_master", "two_year"): "S3",
        # 海外博士
        ("overseas_phd", "general"): "S3",
    }

    key = (education_type, grade)
    return grade_stage_map.get(key, "S1")


def get_stage_info(stage_id: str) -> dict:
    """获取阶段详细信息"""
    return STAGES.get(stage_id, STAGES["S1"])


def get_onboarding_questions() -> list:
    """获取引导问卷题目"""
    return [
        {
            "key": "major_category",
            "title": "你的专业属于哪个大类？",
            "type": "single_choice",
            "options": [
                {"value": "science", "label": "理科（数理化生地统计等）"},
                {"value": "engineering", "label": "工科（计算机、AI、通信、机械等）"},
                {"value": "arts", "label": "文科（文史哲、新闻、艺术等）"},
                {"value": "social_science", "label": "社科（法学、社会学、心理、教育等）"},
                {"value": "business", "label": "商科（金融、经济、会计、管理、市场等）"},
                {"value": "medicine", "label": "医科（临床、药学、护理、公卫等）"},
                {"value": "agriculture_other", "label": "农科及其他（农学、食品、设计、体育等）"},
            ]
        },
        {
            "key": "education_type",
            "title": "你目前的学历和学校类型是？",
            "type": "single_choice",
            "options": [
                {"value": "domestic_bachelor", "label": "国内本科"},
                {"value": "domestic_master", "label": "国内硕士"},
                {"value": "domestic_phd", "label": "国内博士"},
                {"value": "overseas_bachelor", "label": "海外本科（海本）"},
                {"value": "overseas_master", "label": "海外硕士（海硕）"},
                {"value": "overseas_phd", "label": "海外博士（海博）"},
            ]
        },
    ]


def get_grade_options(education_type: str) -> list:
    """根据学历类型返回年级选项（附带对应阶段信息）"""
    from data_definitions import EDUCATION_LEVELS
    edu = EDUCATION_LEVELS.get(education_type, {})
    grades = edu.get("grades", {})
    options = []
    for k, v in grades.items():
        stage = detect_stage(education_type, k)
        stage_info = STAGES.get(stage, {})
        options.append({
            "value": k,
            "label": v.get("name", k),
            "stage": stage,
            "stage_name": stage_info.get("name", ""),
            "stage_emoji": stage_info.get("emoji", ""),
            "stage_desc": v.get("stage", ""),
        })
    return options
