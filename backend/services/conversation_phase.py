"""一步(StepOne) · 四阶段对话框架 · V3.1"""

PHASES = {
    "phase1": {
        "name": "探索期",
        "goal": "帮助用户发现兴趣线索和能量来源",
        "key_questions": [
            "过去有没有哪个时刻，做某件事觉得时间过得很快？",
            "那种感觉来自什么？（创造/协调/分析/帮助他人/...）",
            "如果不考虑钱和面子，你最想尝试什么？",
        ],
        "output": "3-5条兴趣线索",
        "next": "phase2",
    },
    "phase2": {
        "name": "聚焦期",
        "goal": "从兴趣线索中筛选出 1-2 个可探索的方向",
        "key_questions": [
            "这几条线索中，哪一条让你最有冲动去深入了解？",
            "你担心什么？（能力不够/家人反对/不了解行业/...）",
            "如果有一个最小成本的尝试，你愿意做什么？",
        ],
        "output": "1-2个探索方向 + 1个最小尝试",
        "next": "phase3",
    },
    "phase3": {
        "name": "验证期",
        "goal": "通过实际行动验证方向是否匹配",
        "key_questions": [
            "尝试之后，和你想象的一样吗？",
            "哪个瞬间让你觉得'这就是我要的'？",
            "哪个瞬间让你觉得'好像不太对'？",
        ],
        "output": "方向确认/调整 + 人才雷达图初版",
        "next": "phase4",
    },
    "phase4": {
        "name": "行动期",
        "goal": "制定个性化里程碑，开始执行",
        "key_questions": [
            "为了实现这个方向，你觉得第一步应该是什么？",
            "你希望我如何提醒你？（温柔/直接/只在你问时回应）",
            "如果遇到困难，你希望我怎么帮你？",
        ],
        "output": "自定义里程碑 + 叙事故事草稿",
        "next": None,
    },
}

# 对话分支逻辑
RESPONSE_BRANCHES = {
    "clear": {
        "description": "清晰明确型——用户有明确的想法",
        "strategy": "帮助细化，确认真实性",
        "example": "你说想做产品经理，能具体说说你理解的产品经理每天在做什么吗？",
    },
    "hesitant": {
        "description": "模糊犹豫型——用户不确定",
        "strategy": "帮助澄清，降低决策压力",
        "example": "没关系，不需要现在就想清楚。我们可以先花点时间了解一下各个方向具体在做什么。",
    },
    "herd": {
        "description": "跟风从众型——用户说'大家都说好'",
        "strategy": "温和挑战，引导自我反思",
        "example": "大家都说好的，不一定适合你。我想听听你自己是怎么想的？",
    },
    "anxious": {
        "description": "焦虑自我否定型——用户自我贬低",
        "strategy": "情绪兜底，暂停方向讨论",
        "example": "我感觉到你对自己有些苛刻。我们先不聊方向了，说说最近有什么让你开心的小事？",
    },
    "action": {
        "description": "行动导向型——用户想做点什么",
        "strategy": "帮助拆解第一步，避免空想",
        "example": "你很想试试，那这周能不能做一个最小成本的尝试？比如和一个从业者聊15分钟？",
    },
    "challenge_holland": {
        "description": "挑战测评结果——用户觉得测评不准",
        "strategy": "鼓励质疑，深入探索不一致",
        "example": "你说测评结果不太像你——这很有意思。能说说具体哪里不像吗？有时候'不像'的背后，藏着你对自己更深的了解。",
    },
    "agree_holland": {
        "description": "认同测评结果——用户觉得测评很准",
        "strategy": "深入验证，避免自我确认偏差",
        "example": "你觉得结果很准。那我想追问一下——你说喜欢研究（I），能举一个最近的例子吗？有时候我们认为自己'应该是那样'，但实际的感受未必如此。",
    },
}


def detect_branch_type(user_text: str) -> str:
    """根据用户输入判断对话分支类型"""
    # 焦虑/自我否定
    anxiety_keywords = ["我不行", "我太差", "配不上", "比不上", "废物", "没用", "我做不到"]
    for kw in anxiety_keywords:
        if kw in user_text:
            return "anxious"

    # 挑战测评
    challenge_keywords = ["不太像", "不准", "不对", "不像我", "不是这样", "不是我"]
    for kw in challenge_keywords:
        if kw in user_text:
            return "challenge_holland"

    # 认同测评
    agree_keywords = ["好像是我", "挺准的", "确实", "就是这样", "是我"]
    for kw in agree_keywords:
        if kw in user_text:
            return "agree_holland"

    # 跟风从众
    herd_keywords = ["大家都说", "别人都", "他们说", "很多人说", "大家都在", "现在很火"]
    for kw in herd_keywords:
        if kw in user_text:
            return "herd"

    # 行动导向
    action_keywords = ["试试", "想做", "怎么开始", "第一步", "接下来", "现在", "打算", "准备"]
    for kw in action_keywords:
        if kw in user_text:
            return "action"

    # 模糊犹豫
    hesitant_keywords = ["不确定", "不知道", "可能", "也许", "纠结", "不知道选", "犹豫", "再看看"]
    for kw in hesitant_keywords:
        if kw in user_text:
            return "hesitant"

    return "clear"


def get_branch_response(branch_type: str) -> str:
    """获取分支响应策略文本"""
    return RESPONSE_BRANCHES.get(branch_type, RESPONSE_BRANCHES["clear"])


def get_phase_opening(phase: str, memories: list = None) -> str:
    """根据当前对话阶段生成开场白"""
    phase_info = PHASES.get(phase, PHASES["phase1"])

    if phase == "phase1":
        return "Hi！欢迎来到一步。我不打算告诉你要做什么，而是想先了解你——过去有没有哪个时刻，你做某件事的时候觉得时间过得很快、很有满足感？"

    if phase == "phase2":
        return "很好，我们已经发现了一些让你有成就感的线索。现在让我们聚焦一下——这几条线索中，哪一条让你最有冲动去深入了解？"

    if phase == "phase3":
        return "欢迎回来！上次你决定去尝试一下XXX，感觉怎么样？和你想象的一样吗？"

    if phase == "phase4":
        return "恭喜，你已经找到了自己的方向！现在让我们来制定具体的计划——你觉得第一步应该是什么？"

    return "欢迎回来！我们继续聊聊。"


def should_advance_phase(phase: str, interest_clues: list = None, explore_directions: list = None, has_attempt: bool = False) -> tuple:
    """判断是否应该推进对话阶段"""
    if phase == "phase1" and interest_clues and len(interest_clues) >= 3:
        return True, "phase2"
    if phase == "phase2" and explore_directions and len(explore_directions) >= 1:
        return True, "phase3"
    if phase == "phase3" and has_attempt:
        return True, "phase4"
    return False, phase
