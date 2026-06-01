"""一步(StepOne) · 参考案例库 · V3.0
模板不再作为"推荐路径"，而是作为"别人的故事"供用户参考。
每个案例末尾都有明确声明："这是他那个年代、他那个背景的路，仅供参考。"
"""

REFERENCE_CASES = [
    {
        "id": 1,
        "title": "计算机 → 后端开发 → 腾讯",
        "background": "985 计算机本科，大三暑期实习转正",
        "path": "编程语言基础 → 个人项目 → 暑期实习 → 转正答辩 → 秋招收官",
        "key_insight": "他大二暑假做了一个校园二手交易平台，这个项目成了面试的核心谈资",
        "disclaimer": "这是他那个年代、他那个背景的路。现在面试更卷，但好项目的价值不会变。",
        "tags": ["计算机", "互联网", "后端"],
    },
    {
        "id": 2,
        "title": "化学 → 咨询 → 麦肯锡",
        "background": "C9 化学博士，通过 Case Competition 进入咨询",
        "path": "博士期间参加咨询商赛 → 暑期实习 → 秋招 → 麦肯锡",
        "key_insight": "他最大的优势不是化学知识，而是博士训练出的结构化思维和数据敏感度",
        "disclaimer": "博士转行咨询是常见的路径，但每个人转行的原因不同。想清楚你为什么想转，比模仿别人更重要。",
        "tags": ["化学", "咨询", "博士"],
    },
    {
        "id": 3,
        "title": "英语 → 游戏本地化 → 米哈游",
        "background": "普通一本英语专业，对游戏极度热爱",
        "path": "自学游戏本地化工具 → 做独立游戏翻译志愿者 → 暑期实习 → 秋招",
        "key_insight": "她在B站做了很多游戏翻译对比视频，积累了自己的作品集，面试时直接展示了这些",
        "disclaimer": "这是一条非常规的路径。游戏行业招人很看作品集和热情，学历反而是次要的。",
        "tags": ["英语", "游戏", "文科"],
    },
    {
        "id": 4,
        "title": "金融 → 互联网产品 → 字节跳动",
        "background": "海本金融，大二暑假在投行实习后发现不喜欢",
        "path": "投行实习（发现不喜欢）→ 自学产品知识 → 产品实习 → 秋招转产品",
        "key_insight": "他最大的转折点是：承认自己不喜欢金融，而不是硬撑。投行经历反而成了他'跨界思维'的亮点",
        "disclaimer": "不是所有人都能在投行实习后还能转产品。他的优势在于行动力——发现不喜欢就立刻找新方向，而不是纠结。",
        "tags": ["金融", "互联网", "产品", "海本"],
    },
    {
        "id": 5,
        "title": "社会学 → 用户研究 → 互联网大厂",
        "background": "211 社会学硕士，从未学过代码",
        "path": "学术研究方法论 → 用研实习 → 秋招 → 用户研究员",
        "key_insight": "她把学术访谈、问卷设计、质性分析的方法论直接迁移到了用研工作中，这是技术背景的人不具备的",
        "disclaimer": "用研岗位在国内需求较小但竞争也相对小。这条路适合真的喜欢理解'人为什么这样做'的人。",
        "tags": ["社会学", "互联网", "用户研究", "社科"],
    },
]


def get_cases_by_tag(tag: str = "") -> list:
    """按标签筛选参考案例"""
    if not tag:
        return REFERENCE_CASES
    return [c for c in REFERENCE_CASES if tag in c.get("tags", [])]


def get_case_context_for_ai(major_category: str = "") -> str:
    """生成给 AI 的参考案例上下文"""
    if not major_category:
        return ""

    cases = [c for c in REFERENCE_CASES if major_category in c.get("tags", []) or any(
        t in str(c.get("tags", [])) for t in ["互联网", "咨询", "金融", "游戏", "产品"]
    )]

    if not cases:
        cases = REFERENCE_CASES[:2]

    context = "## 参考案例（仅供对话中引用，不要直接推荐）\n"
    for c in cases[:3]:
        context += f"\n📖 {c['title']}\n"
        context += f"   TA走了：{c['path']}\n"
        context += f"   关键发现：{c['key_insight']}\n"
        context += f"   ⚠️ {c['disclaimer']}\n"

    return context
