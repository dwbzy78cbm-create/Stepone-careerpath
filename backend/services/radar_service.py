"""一步(StepOne) · 人才雷达图引擎 · V3.3
双图层结构：理论框架层（霍兰德）+ 对话特质层（AI挖掘）
"""
import json
import httpx
from config import AI_API_KEY, AI_API_BASE, AI_MODEL

# 特质关键词映射库
TRAIT_MAP = {
    # 秩序/结构类
    "理顺": "秩序感", "整理": "秩序感", "规划": "秩序感", "条理": "秩序感",
    "流程": "秩序感", "组织": "秩序感", "协调": "秩序感", "安排": "秩序感",
    # 好奇/钻研类
    "好奇": "好奇心", "深挖": "好奇心", "追根究底": "好奇心", "探索": "好奇心",
    "研究": "好奇心", "分析": "好奇心", "意外发现": "好奇心", "刨根问底": "好奇心",
    # 同理/助人类
    "帮助": "同理心", "理解别人": "同理心", "共情": "同理心", "倾听": "同理心",
    "照顾": "同理心", "支持": "同理心", "体谅": "同理心", "关心": "同理心",
    # 创新/创意类
    "创意": "创新性", "创新": "创新性", "新方法": "创新性", "不一样": "创新性",
    "尝试": "创新性", "设计": "创新性", "创造": "创新性", "想象": "创新性",
    # 执行/行动类
    "执行": "执行力", "完成": "执行力", "做到": "执行力", "落地": "执行力",
    "行动": "执行力", "实现": "执行力", "交付": "执行力", "推进": "执行力",
    # 数据/逻辑类
    "数据": "数据敏感度", "逻辑": "逻辑思维", "推理": "逻辑思维", "量化": "数据敏感度",
    "数字": "数据敏感度", "统计": "数据敏感度", "编程": "技术能力", "代码": "技术能力",
    # 沟通/表达类
    "沟通": "沟通力", "表达": "沟通力", "说服": "沟通力", "演讲": "沟通力",
    "汇报": "沟通力", "写作": "文字表达", "写": "文字表达", "文案": "文字表达",
    # 领导/影响类
    "领导": "领导力", "带领": "领导力", "影响": "领导力", "统筹": "领导力",
    "负责": "领导力", "管理": "领导力",
}


def extract_traits_from_text(text: str) -> list:
    """从文本中提取特质关键词"""
    found = {}
    for keyword, trait in TRAIT_MAP.items():
        if keyword in text:
            found[trait] = found.get(trait, 0) + 1

    # 按出现频次排序，取前 7 个
    sorted_traits = sorted(found.items(), key=lambda x: x[1], reverse=True)
    return [{"name": name, "mentions": count} for name, count in sorted_traits[:7]]


def extract_traits_from_messages(messages: list[str]) -> list:
    """从多轮对话中聚合提取特质"""
    all_traits = {}
    for msg in messages:
        for keyword, trait in TRAIT_MAP.items():
            if keyword in msg:
                all_traits[trait] = all_traits.get(trait, 0) + 1

    sorted_traits = sorted(all_traits.items(), key=lambda x: x[1], reverse=True)[:7]
    max_count = sorted_traits[0][1] if sorted_traits else 1

    return [
        {
            "name": name,
            "confidence": round(count / max_count * 100, 1),
            "description": _get_trait_description(name),
        }
        for name, count in sorted_traits
    ]


def _get_trait_description(trait_name: str) -> str:
    """获取特质描述"""
    descriptions = {
        "秩序感": "在混乱中能保持冷静，找到规律和秩序",
        "好奇心": "对未知有天然的兴趣，喜欢深入探索",
        "同理心": "能很快理解他人的情绪和需求",
        "创新性": "喜欢尝试新方法，不满足于按部就班",
        "执行力": "想到就去做，能把想法落地为行动",
        "数据敏感度": "能从数字中发现规律和洞察",
        "逻辑思维": "善于推理和分析，结构清晰",
        "技术能力": "具备编程和技术实现的动手能力",
        "沟通力": "能清晰表达想法，有效传递信息",
        "文字表达": "擅长用文字表达思想，写作能力强",
        "领导力": "能带领团队、统筹资源达成目标",
    }
    return descriptions.get(trait_name, "基于对话中你的表现")


async def generate_radar_with_ai(
    messages: list[str],
    milestones: list = None,
    stories: list = None,
) -> dict:
    """使用 AI 深度生成雷达图（对话内容较多时使用）"""
    if not AI_API_KEY or AI_API_KEY == "your-api-key-here":
        return _fallback_radar(messages)

    # 先用本地提取做基础
    local_traits = extract_traits_from_messages(messages)
    if len(local_traits) < 3:
        return _fallback_radar(messages)

    context = f"用户对话摘要：{' '.join(messages[-5:])}"

    system_prompt = """你是一位职业特质分析师，擅长从对话中挖掘用户的独特特质。

## 任务
从用户的对话内容中提取 5-7 个最突出的特质维度，为每个维度写一句描述性解读（不是分数，是描述）。

## 输出格式（JSON）
{
  "dimensions": [
    {"name": "秩序感", "description": "在混乱中能保持冷静，找到规律", "confidence": 85},
    {"name": "好奇心", "description": "对未知有天然的兴趣，喜欢深挖", "confidence": 78}
  ],
  "interpretation": "基于对话的整体解读（100字内）",
  "disclaimer": "这只是基于目前对话的初步观察，随着我们聊得更多，这张图会不断进化。"
}

## 注意
- 不要给分数（如"7/10"），只给描述和置信度
- 特质名称使用中文，如"秩序感""好奇心""同理心""创新性""执行力"
- interpretation 用第二人称"你"来写"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{AI_API_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context},
                    ],
                    "max_tokens": 600,
                    "temperature": 0.7,
                },
            )
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                try:
                    # 尝试提取 JSON
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    if start >= 0 and end > start:
                        return json.loads(content[start:end])
                except json.JSONDecodeError:
                    pass
    except Exception:
        pass

    return _fallback_radar(messages)


def _fallback_radar(messages: list[str]) -> dict:
    """本地兜底雷达图生成"""
    traits = extract_traits_from_messages(messages)
    if len(traits) < 3:
        traits = [
            {"name": "执行力", "confidence": 50, "description": "能按计划推进任务"},
            {"name": "好奇心", "confidence": 50, "description": "对新知识保持开放态度"},
            {"name": "沟通力", "confidence": 50, "description": "能清晰表达自己的想法"},
        ]

    return {
        "framework_layer": [],
        "dialogue_layer": [{"name": t["name"], "source": "对话挖掘", "description": t["description"], "confidence": t["confidence"]} for t in traits],
        "dimensions": traits,
        "interpretation": "基于目前对话，你展现了这些特质。",
        "disclaimer": "这只是基于目前对话的初步观察。",
    }


def merge_radar_layers(framework_layer: list, dialogue_layer: list, holland_top_types: list = None) -> dict:
    """合并理论框架层和对话特质层，生成完整雷达图"""
    # 去重：对话层中与框架层相似的特质不重复显示
    framework_names = {f["name"].split()[-1] if " " in f["name"] else f["name"] for f in framework_layer}
    filtered_dialogue = [d for d in dialogue_layer if d.get("name", "") not in framework_names]

    all_dimensions = framework_layer + filtered_dialogue

    # 合并为前端可用格式
    dimensions = []
    for item in all_dimensions:
        dim = {
            "name": item.get("name", ""),
            "source": item.get("source", "霍兰德测评" if item in framework_layer else "对话挖掘"),
            "description": item.get("description", ""),
            "confidence": item.get("confidence", 50),
            "layer": "framework" if item in framework_layer else "dialogue",
        }
        dimensions.append(dim)

    interpretation_parts = []
    if framework_layer:
        fw_names = [f["name"] for f in framework_layer]
        interpretation_parts.append(f"测评框架：{', '.join(fw_names)}")
    if filtered_dialogue:
        dl_names = [d["name"] for d in filtered_dialogue]
        interpretation_parts.append(f"对话发现：{', '.join(dl_names)}")

    return {
        "framework_layer": framework_layer,
        "dialogue_layer": filtered_dialogue,
        "dimensions": dimensions,
        "interpretation": "；".join(interpretation_parts) if interpretation_parts else "雷达图生成中...",
        "disclaimer": "这张图会随着我们的对话继续进化。测评给了你一个坐标，但对话填上了独一无二的你。",
        "holland_top_types": holland_top_types,
    }


def get_role_matches(traits: list) -> list:
    """基于特质匹配岗位"""
    trait_names = [t["name"] for t in traits]

    role_map = {
        "产品经理": ["同理心", "逻辑思维", "沟通力", "创新性"],
        "数据分析师": ["数据敏感度", "逻辑思维", "好奇心", "执行力"],
        "后端开发": ["技术能力", "逻辑思维", "秩序感", "执行力"],
        "用户研究员": ["同理心", "好奇心", "沟通力", "逻辑思维"],
        "管理咨询": ["逻辑思维", "沟通力", "领导力", "创新性"],
        "内容运营": ["文字表达", "同理心", "创新性", "执行力"],
    }

    matches = []
    for role, required in role_map.items():
        score = sum(1 for t in required if t in trait_names)
        if score >= 2:
            matches.append({"role": role, "match_points": score, "matched_traits": [t for t in required if t in trait_names]})

    return sorted(matches, key=lambda x: x["match_points"], reverse=True)[:3]
