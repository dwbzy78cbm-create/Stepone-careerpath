"""一步(StepOne) · 霍兰德 RIASEC 精简测评 · V3.3"""

# 12 题精简版霍兰德测评
HOLLAND_QUESTIONS = [
    {"id": 1, "option_a": "动手修理东西", "type_a": "R", "option_b": "阅读科学文章", "type_b": "I"},
    {"id": 2, "option_a": "画一幅画", "type_a": "A", "option_b": "组织一场活动", "type_b": "E"},
    {"id": 3, "option_a": "分析数据找规律", "type_a": "I", "option_b": "帮助朋友解决问题", "type_b": "S"},
    {"id": 4, "option_a": "按流程精确完成", "type_a": "C", "option_b": "说服别人接受观点", "type_b": "E"},
    {"id": 5, "option_a": "户外动手操作", "type_a": "R", "option_b": "独立做研究", "type_b": "I"},
    {"id": 6, "option_a": "创作设计", "type_a": "A", "option_b": "培训指导他人", "type_b": "S"},
    {"id": 7, "option_a": "解决复杂逻辑问题", "type_a": "I", "option_b": "带领团队达成目标", "type_b": "E"},
    {"id": 8, "option_a": "整理文件数据", "type_a": "C", "option_b": "自由发挥创意", "type_b": "A"},
    {"id": 9, "option_a": "使用工具器械", "type_a": "R", "option_b": "与人深度交流", "type_b": "S"},
    {"id": 10, "option_a": "欣赏艺术作品", "type_a": "A", "option_b": "遵守规则流程", "type_b": "C"},
    {"id": 11, "option_a": "探索科学现象", "type_a": "I", "option_b": "创业或做生意", "type_b": "E"},
    {"id": 12, "option_a": "帮助弱势群体", "type_a": "S", "option_b": "管理财务预算", "type_b": "C"},
]

HOLLAND_TYPES = {
    "R": {"name": "实际型", "keyword": "动手、操作、工具、户外",
          "description": "喜欢动手操作、使用工具、户外活动，偏好具体可见的成果",
          "careers": ["工程师", "技术员", "建筑师", "飞行员", "外科医生", "机械师"]},
    "I": {"name": "研究型", "keyword": "思考、分析、探索、逻辑",
          "description": "喜欢观察、分析、探索和解决问题，对科学和理论有兴趣",
          "careers": ["科学家", "数据分析师", "研究员", "医生", "算法工程师", "战略分析师"]},
    "A": {"name": "艺术型", "keyword": "创造、表达、自由、美感",
          "description": "喜欢创造、表达自我，偏好自由灵活的工作方式",
          "careers": ["设计师", "作家", "艺术家", "内容创作者", "产品经理", "UX设计师"]},
    "S": {"name": "社会型", "keyword": "助人、教学、沟通、合作",
          "description": "喜欢帮助他人、教学培训、与人深度交流",
          "careers": ["教师", "心理咨询师", "HR", "社工", "医生", "客户经理", "用户研究员"]},
    "E": {"name": "企业型", "keyword": "领导、说服、决策、冒险",
          "description": "喜欢领导、说服、管理和创业，偏好有挑战和竞争的环境",
          "careers": ["企业家", "管理者", "销售经理", "律师", "投资银行家", "政治家"]},
    "C": {"name": "常规型", "keyword": "秩序、细节、规范、精确",
          "description": "喜欢有序、规范的工作，注重细节和精确性",
          "careers": ["会计", "审计", "行政", "数据分析", "质量控制", "银行柜员"]},
}

# 霍兰德类型组合 → 适配岗位
HOLLAND_ROLE_MAP = {
    ("I", "R"): ["工程师", "技术研究员", "医生", "数据工程师"],
    ("I", "S"): ["数据分析师(偏业务)", "用户研究员", "教育产品经理", "医生", "技术培训师"],
    ("I", "A"): ["游戏策划", "数据可视化设计师", "建筑师", "UX研究员"],
    ("I", "C"): ["数据分析师", "精算师", "质量控制工程师", "研究助理"],
    ("I", "E"): ["技术管理", "咨询顾问", "产品策略", "技术创业"],
    ("S", "E"): ["项目经理", "销售经理", "HRBP", "教育管理者", "公关"],
    ("S", "A"): ["用户体验设计师", "内容策划", "艺术治疗师", "教育设计师"],
    ("S", "C"): ["行政主管", "客户服务管理", "社会工作", "教务管理"],
    ("A", "E"): ["产品经理", "创业者", "广告创意", "品牌经理", "艺术总监"],
    ("A", "C"): ["UI设计师", "编辑", "博物馆管理", "设计管理"],
    ("R", "E"): ["工程项目经理", "制造业管理", "建筑项目经理", "技术销售"],
    ("R", "C"): ["质量控制", "技术员", "设备管理", "安全工程师"],
    ("E", "C"): ["投行分析师", "律师", "管理咨询", "财务经理", "审计经理"],
    ("R", "A"): ["工业设计师", "建筑设计师", "景观设计师", "游戏关卡设计"],
    ("R", "S"): ["物理治疗师", "教练", "技术培训", "消防员", "护理"],
}


def calculate_holland(answers: list) -> dict:
    """计算霍兰德测评结果
    answers: [{"question_id": 1, "choice": "a"}, ...]
    返回: {"R": 3, "I": 5, "A": 1, "S": 2, "E": 1, "C": 0}
    """
    scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}

    for answer in answers:
        qid = answer.get("question_id") or answer.get("id")
        choice = answer.get("choice", "a")
        for q in HOLLAND_QUESTIONS:
            if q["id"] == qid:
                if choice == "a":
                    scores[q["type_a"]] += 1
                else:
                    scores[q["type_b"]] += 1
                break

    # 找出前两个最高分
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_types = sorted_types[:2]

    # 匹配岗位
    type_key = tuple(sorted([t[0] for t in top_types]))
    matched_roles = HOLLAND_ROLE_MAP.get(type_key, [])
    if not matched_roles:
        # 尝试反向顺序
        type_key_rev = tuple(sorted([t[0] for t in top_types], reverse=True))
        matched_roles = HOLLAND_ROLE_MAP.get(type_key_rev, ["通用岗位"])

    return {
        "scores": scores,
        "top_types": [{"type": t[0], "name": HOLLAND_TYPES[t[0]]["name"],
                       "score": t[1], "description": HOLLAND_TYPES[t[0]]["description"],
                       "careers": HOLLAND_TYPES[t[0]]["careers"]} for t in top_types],
        "matched_roles": matched_roles,
        "all_types": [{"type": k, "name": v["name"], "score": scores[k],
                        "keyword": v["keyword"], "description": v["description"]}
                      for k, v in HOLLAND_TYPES.items()],
    }


def generate_initial_radar(holland_result: dict) -> dict:
    """从霍兰德测评结果生成初始雷达图（理论框架层）"""
    top = holland_result.get("top_types", [])
    all_types = holland_result.get("all_types", [])

    # 理论框架层：霍兰德 6 维度
    framework_layer = [
        {
            "name": f"{t['type']} {t['name']}",
            "source": "霍兰德测评",
            "description": t["description"],
            "confidence": min(t["score"] * 25, 100),  # 最高4分→100%
        }
        for t in all_types if t["score"] > 0
    ]

    return {
        "framework_layer": framework_layer,
        "dialogue_layer": [],
        "top_types": top,
        "matched_roles": holland_result.get("matched_roles", []),
        "interpretation": _generate_initial_interpretation(top),
        "disclaimer": "这只是基于12道题的初步参考，不是对你的定义。接下来，我们聊聊——这是真的你吗？",
    }


def _generate_initial_interpretation(top_types: list) -> str:
    """生成初始雷达图的AI解读"""
    if len(top_types) < 2:
        return "测评结果还在收集中..."
    t1 = top_types[0]
    t2 = top_types[1]
    return (
        f"测评显示你最突出的两个倾向是{t1['name']}（{t1['description'][:20]}...）"
        f"和{t2['name']}（{t2['description'][:20]}...）。"
        f"但这是真的你吗？还是'你以为的你'？还是'别人期待的你'？"
        f"接下来我们聊聊。"
    )


def get_questions() -> list:
    """获取所有霍兰德测评题目"""
    return HOLLAND_QUESTIONS
