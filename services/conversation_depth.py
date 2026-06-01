"""五层简历加工流水线 —— V4.1

核心理念：用户下命令，AI 执行任务，逐层推进产出结果。

推进规则（AI 必须遵守）：
- 每层收集够信息就立刻推下一层，不要反复追问同类问题
- 推进时用推进语明确告诉用户"我们现在进入下一阶段"

深度1: 描述经历 → 用户扔经历，AI 整理归类
深度2: 确认目标 → 用户说想投什么岗位，AI 分析匹配度
深度3: 拆解经历 → AI 追问每段经历的细节和数据
深度4: STAR转译 → AI 直接输出 STAR 格式的简历条目（叙事重构在此完成）
深度5: 行动建议 → AI 给出投递策略和面试预测
"""

DEPTH_DEFINITIONS = {
    "depth1": {
        "id": "depth1",
        "name": "描述经历",
        "description": "用户把做过的项目、实习、比赛等经历告诉AI，AI接收并归类",
        "goal": "收集至少2-3段经历素材",
        "user_does": "说：我做过XX项目、XX实习、XX比赛...",
        "ai_does": "逐条接收 → 归类（项目/实习/竞赛/社团）→ 追问'还有吗？'",
        "ai_output": "一份按类别整理的经历清单",
        "push_keywords": ["还有吗", "继续", "其他的呢", "还有别的经历吗", "再想想"],
        "done_signal": "用户说'差不多就这些''没了''暂时这些'，或已收集2段以上",
        "push_line": "经历收到了。你想投什么岗位？或者对哪些方向感兴趣？",
        "opening_lines": [
            "把你做过的项目、实习、比赛、社团活动告诉我，越详细越好。我来帮你整理。",
            "直接扔经历给我就行，比如'我做过XX项目，负责前端开发'。",
        ],
        "example_dialogue": [
            "用户: 我做过一个电商小程序，负责前端开发。",
            "AI: 收到。电商小程序，前端开发。还有吗？实习、比赛、课程项目都算。",
            "用户: 还有一个数据分析比赛，拿了二等奖。",
            "AI: 已记录。电商小程序（前端）+ 数据分析比赛（二等奖）。继续，还有吗？",
        ],
        "transition_signals": [
            "用户至少提供了2-3段经历",
            "用户说'差不多就这些'/'没了'/'暂时想到这些'",
        ],
        "next_depth": "depth2",
    },
    "depth2": {
        "id": "depth2",
        "name": "确认目标",
        "description": "了解用户想投什么岗位，分析经历匹配度",
        "goal": "确定求职目标方向",
        "user_does": "说：我想投XX岗位/XX行业",
        "ai_does": "分析已有经历和岗位的匹配度 → 指出哪些经历有价值 → 指出还缺什么",
        "ai_output": "匹配分析 + 缺口提示",
        "push_keywords": ["你想投什么岗位", "目标方向", "感兴趣的方向", "想做什么"],
        "done_signal": "用户明确了岗位方向",
        "push_line": "好的。现在我们逐段深挖细节，先从你最对口的经历开始。",
        "opening_lines": [
            "经历收到了。你想投什么岗位？或者对哪些行业感兴趣？",
        ],
        "example_dialogue": [
            "用户: 我想投前端开发。",
            "AI: 电商小程序直接匹配前端岗。数据分析比赛可作为数据敏感度的加分项。还缺团队协作经历，有没有小组项目？",
        ],
        "transition_signals": ["用户明确了求职目标", "AI 已完成匹配分析"],
        "next_depth": "depth3",
    },
    "depth3": {
        "id": "depth3",
        "name": "拆解经历",
        "description": "对每段经历追问细节：具体做了什么、解决了什么问题、有什么数据成果",
        "goal": "挖出每段经历的量化数据和隐性亮点",
        "user_does": "回答AI追问：具体功能、技术难点、数据成果",
        "ai_does": "逐段追问 → 要数据（优化了多少？团队几人？你负责什么？）→ 发现亮点",
        "ai_output": "每段经历的详细拆解：背景、动作、难点、成果、数据",
        "push_keywords": ["具体说说", "数据是多少", "几个人做的", "你负责哪些", "有没有遇到难点", "优化了多少"],
        "done_signal": "关键经历细节已挖够，有量化数据",
        "push_line": "拆解完毕。现在把你的经历转成简历语言。",
        "opening_lines": [
            "逐段深挖。先从最对口的经历开始——具体做了哪些功能？有没有性能优化？数据是多少？",
        ],
        "example_dialogue": [
            "AI: 电商小程序——具体实现了哪些功能？",
            "用户: 商品列表、购物车、订单页。",
            "AI: 有性能优化吗？加载时间优化了多少？",
            "用户: 做了虚拟列表，加载从3秒降到0.5秒。",
            "AI: 这是亮点。拆解完毕，现在帮你转成简历语言。",
        ],
        "transition_signals": ["关键经历的细节已挖够", "用户说'差不多了'"],
        "next_depth": "depth4",
    },
    "depth4": {
        "id": "depth4",
        "name": "STAR转译",
        "description": "将拆解后的经历直接输出为 STAR 格式的简历条目（叙事重构在此完成）",
        "goal": "输出可直接复制到简历的 STAR 条目",
        "user_does": "确认和微调 AI 输出的简历条目",
        "ai_does": "逐段输出 STAR 格式 → 控制每条3行以内 → 突出量化结果 → 对齐岗位关键词",
        "ai_output": "STAR 简历条目 + 技能关键词",
        "push_keywords": ["STAR版本", "简历语言", "转成", "S情境", "T任务", "A行动", "R结果"],
        "done_signal": "主要经历的 STAR 条目已生成并确认",
        "push_line": "简历内容准备好了。现在帮你规划下一步行动。",
        "opening_lines": [
            "现在把你的经历转成简历语言，每条按 STAR 格式输出：",
        ],
        "example_dialogue": [
            "AI: 电商小程序 →",
            "【S】独立负责电商小程序前端开发，含商品列表、购物车、订单管理",
            "【T】解决商品列表大量数据下的卡顿问题",
            "【A】采用虚拟列表方案，按需渲染",
            "【R】加载时间从3秒降至0.5秒",
            "用户: 购物车还做了库存校验。",
            "AI: 加上。【A】实现了购物车库存实时校验逻辑。",
        ],
        "transition_signals": ["主要经历的 STAR 条目已生成", "用户确认完毕"],
        "next_depth": "depth5",
    },
    "depth5": {
        "id": "depth5",
        "name": "行动建议",
        "description": "基于经历和目标岗位，给出投递策略、补强建议、面试预测",
        "goal": "产出可执行的下一步行动计划",
        "user_does": "了解接下来该干嘛",
        "ai_does": "评估竞争力 → 推荐投递策略 → 指出技能缺口 → 预测面试问题",
        "ai_output": "投递建议 + 补强清单 + 面试预测题",
        "push_keywords": ["投递", "补强", "面试", "下一步", "行动计划"],
        "done_signal": "行动计划已输出",
        "push_line": None,
        "opening_lines": [
            "简历素材准备好了。帮你规划下一步：",
        ],
        "example_dialogue": [
            "AI: 基于你的经历和目标（前端开发）：",
            "【投递】匹配度约70%，建议优先投React技术栈的中小厂。",
            "【补强】缺团队项目经历，建议参与开源项目。",
            "【面试】面试官大概率会问虚拟列表实现原理，准备一下。",
        ],
        "transition_signals": [],
        "next_depth": None,
    },
}

# V4.1: 极低阈值——任务驱动模式，AI 主动推进
DEPTH_TRANSITIONS = {
    "depth1": {"to": "depth2", "min_messages": 2, "min_user_messages": 1},
    "depth2": {"to": "depth3", "min_messages": 4, "min_user_messages": 2},
    "depth3": {"to": "depth4", "min_messages": 6, "min_user_messages": 3},
    "depth4": {"to": "depth5", "min_messages": 8, "min_user_messages": 4},
}

# V4.1: 工具入口触发条件
# depth4 = STAR转译完成 → 显示"生成简历"
# depth5 = 行动建议 → 显示"面试准备"
TOOL_ENTRY_CONDITIONS = {
    "resume": {"min_depth": "depth4", "min_user_messages": 3},
    "interview": {"min_depth": "depth5", "min_user_messages": 4},
}

# 叙事入口简化为：depth4 就触发，直接展示简历内容
NARRATIVE_ENTRY_CONDITIONS = {
    "min_depth": "depth4",
    "min_user_messages": 3,
    "description": "STAR转译完成后显示叙事入口",
}

NARRATIVE_TRIGGER_KEYWORDS = [
    "帮我写简历", "生成简历", "整理简历", "做简历",
    "帮我整理经历", "帮我梳理经历", "梳理项目",
    "总结经历", "整理项目", "挖掘经历",
    "STAR", "star", "STAR拆解", "star法则",
    "拆解经历", "拆解项目",
    "叙事重构", "我的故事", "回顾经历", "复盘",
    "看看我做了什么", "分析经历", "分析项目",
    "帮我看看", "帮我改简历",
]
