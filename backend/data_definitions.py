"""三维用户画像数据定义：专业、学历、阶段"""

# ============ 第一维：专业类型 ============
MAJOR_CATEGORIES = {
    "science": {
        "name": "理科",
        "majors": [
            "数学与应用数学", "信息与计算科学", "物理学", "应用物理学",
            "化学", "应用化学", "生物科学", "生物技术", "地理科学",
            "大气科学", "统计学", "应用统计学", "天文学", "地球物理学"
        ],
        "career_directions": [
            "数据分析/数据科学", "科研院所/高校教师", "金融量化分析",
            "IT/互联网技术岗", "教育培训", "生物医药研发", "环境科学"
        ]
    },
    "engineering": {
        "name": "工科",
        "majors": [
            "计算机科学与技术", "软件工程", "人工智能", "电子信息工程",
            "通信工程", "自动化", "机械工程", "土木工程", "材料科学与工程",
            "化学工程与工艺", "生物医学工程", "环境工程", "航空航天工程",
            "电气工程及其自动化", "车辆工程", "测控技术与仪器"
        ],
        "career_directions": [
            "互联网/软件开发", "AI/机器学习工程师", "通信/5G", "智能制造",
            "芯片/半导体", "新能源汽车", "航空航天", "建筑/基建",
            "产品经理", "技术咨询"
        ]
    },
    "arts": {
        "name": "文科",
        "majors": [
            "汉语言文学", "英语", "日语", "法语", "德语", "历史学",
            "哲学", "新闻学", "广告学", "艺术学", "戏剧影视文学",
            "广播电视学", "网络与新媒体", "文物与博物馆学"
        ],
        "career_directions": [
            "新媒体/内容运营", "品牌/市场营销", "编辑/出版", "教育培训",
            "公关/广告", "翻译/外事", "文化/艺术管理", "互联网运营"
        ]
    },
    "social_science": {
        "name": "社科",
        "majors": [
            "法学", "社会学", "心理学", "政治学与行政学", "国际关系",
            "教育学", "公共管理", "社会工作", "行政管理", "劳动与社会保障"
        ],
        "career_directions": [
            "法律/法务", "人力资源管理", "公共管理/公务员", "心理咨询",
            "用户研究/UX研究", "政策研究", "社会组织/NGO", "管理咨询"
        ]
    },
    "business": {
        "name": "商科",
        "majors": [
            "金融学", "经济学", "会计学", "工商管理", "市场营销",
            "国际经济与贸易", "人力资源管理", "财务管理", "保险学",
            "审计学", "物流管理", "电子商务"
        ],
        "career_directions": [
            "投资银行/证券", "商业银行", "四大会计师事务所", "管理咨询",
            "互联网商业分析", "快消/品牌管理", "PE/VC/FA", "企业财务"
        ]
    },
    "medicine": {
        "name": "医科",
        "majors": [
            "临床医学", "基础医学", "药学", "护理学", "公共卫生",
            "口腔医学", "中医学", "医学检验技术", "医学影像学", "麻醉学"
        ],
        "career_directions": [
            "医院/临床医生", "医药研发/药企", "医疗器械", "公共卫生",
            "医疗保险", "医学编辑", "互联网医疗", "生物科技"
        ]
    },
    "agriculture_other": {
        "name": "农科及其他",
        "majors": [
            "农学", "林学", "水产养殖学", "食品科学与工程",
            "设计学", "体育学", "音乐学", "美术学"
        ],
        "career_directions": [
            "农业科技", "食品行业", "设计/UI/UX", "体育产业",
            "文化艺术", "教育", "公务员/事业单位", "互联网/通用岗位"
        ]
    }
}

# ============ 第二维：学历与院校类型 ============
EDUCATION_LEVELS = {
    "domestic_bachelor": {
        "name": "国内本科",
        "duration": 4,
        "grades": {
            "freshman": {
                "name": "大一",
                "stage": "适应大学生活，对专业和职业几乎无概念，纯探索期",
                "key_months": "9月入学，寒假可做短期体验，暑假可参与社会实践",
                "advice": "这个阶段最重要的是打开视野。建议参与社团活动，了解学长学姐的出路，尝试各类通识课程找到兴趣点。"
            },
            "sophomore": {
                "name": "大二",
                "stage": "专业课程深入，开始思考方向，部分同学开始第一份实习",
                "key_months": "暑期实习小规模试水，5-6月投递",
                "advice": "开始建立专业能力护城河。建议参与学科竞赛、创新创业项目，暑期可尝试短期实习或实践项目。"
            },
            "junior": {
                "name": "大三",
                "stage": "核心分流期：暑期实习、考研备考、留学准备三线并行",
                "key_months": "3-5月暑期实习投递高峰，9-10月秋招提前批，12月考研",
                "advice": "这是最关键的决策年。如果求职，暑期实习是进入大厂的最短路径；如果深造，需要全力备考。建议尽早明确方向，避免三线作战。"
            },
            "senior": {
                "name": "大四",
                "stage": "秋招/春招/考研复试/毕设，多重压力叠加",
                "key_months": "9-10月秋招高峰，2-4月春招，3-4月考研复试调剂",
                "advice": "抓住秋招和春招两个窗口期。秋招是最大的机会窗口，春招是补录捡漏的机会。如果考研失利，立刻转入春招。"
            },
            "fifth_year": {
                "name": "大五（建筑/医学等）",
                "stage": "长学制专业，节奏后移一年",
                "key_months": "参照大四节奏",
                "advice": "建筑/医学等专业学制长，但行业认知和实习积累不能等到最后一年。建议大四开始有意识积累行业认知。"
            }
        }
    },
    "domestic_master": {
        "name": "国内硕士",
        "duration": 2,
        "grades": {
            "year1": {
                "name": "研一",
                "stage": "课程为主 + 方向探索，时间紧张（多数只有2-3年）",
                "key_months": "入学即需思考方向，寒假可投日常实习",
                "advice": "硕士时间很短，第一年就要明确求职方向。如果是两年制，研一暑假的实习至关重要；如果是三年制，研二暑假是核心窗口。"
            },
            "year2": {
                "name": "研二",
                "stage": "实习 + 求职核心期（三年制硕士最关键的窗口）",
                "key_months": "3-5月暑期实习投递，9-10月秋招，2-4月春招",
                "advice": "全力以赴的求职季。暑期实习是进入好公司的最佳跳板，秋招是规模最大的招聘窗口。建议提前3个月开始准备简历和面试。"
            },
            "year3": {
                "name": "研三",
                "stage": "秋招收尾/春招冲刺/博士转段/论文答辩",
                "key_months": "秋招最后机会，春招补录",
                "advice": "最后的求职窗口。如果秋招还没拿到满意Offer，春招要更精准地投递，同时做好论文和答辩的时间管理。"
            }
        }
    },
    "domestic_phd": {
        "name": "国内博士",
        "duration": 5,
        "grades": {
            "year1_2": {
                "name": "博一 - 博二",
                "stage": "科研积累期，课程 + 论文 + 实验室",
                "key_months": "暑期可考虑工业界实习（Research Intern）",
                "advice": "博一博二是打基础阶段。如果目标是工业界，建议暑假去大厂做Research Intern建立连接；如果目标是学术界，全力发高水平论文。"
            },
            "year3_4": {
                "name": "博三 - 博四",
                "stage": "国际交流、产学研选择、职业方向分化",
                "key_months": "Research岗秋招，学术 vs 工业界决策点",
                "advice": "职业方向的关键分水岭。学术界关注高校教职招聘（全年滚动），工业界关注大厂Research岗秋招。建议两条线都尝试。"
            },
            "year5_plus": {
                "name": "博五+",
                "stage": "论文收尾 + 求职 + 博士后申请",
                "key_months": "高校教职（全年滚动）、工业界Research岗（秋招为主）",
                "advice": "最后的冲刺阶段。同时推进论文答辩和求职，做好时间规划至关重要。如果暂时没找到合适的教职，博士后是很好的过渡。"
            }
        }
    },
    "overseas_bachelor": {
        "name": "海外本科（海本）",
        "duration": 4,
        "grades": {
            "freshman": {
                "name": "Freshman（大一）",
                "stage": "探索适应期，选专业/转专业窗口",
                "key_months": "9月秋季入学，寒假探索，暑假可做志愿者/短期项目",
                "advice": "海本大一是探索和适应的关键期。利用通识教育体系广泛探索兴趣，了解所学专业在国内外的职业出路。暑假可参与志愿者或短期项目积累经验。"
            },
            "sophomore": {
                "name": "Sophomore（大二）",
                "stage": "专业确认，开始第一份实习探索",
                "key_months": "Spring学期可投递中小公司实习，大二暑假需开始关注投行/咨询的早期项目",
                "advice": "大二是分水岭。建议开始投递中小公司的实习积累经验。如果目标是投行或咨询，大二暑假的早期项目（如Spring Week、Insight Program）是关键跳板。"
            },
            "junior": {
                "name": "Junior（大三）",
                "stage": "核心暑期实习关键年",
                "key_months": "前一年8-10月投递次年Summer Intern（投行/咨询/大厂），这是最重要的一波",
                "advice": "海本最重要的求职年！大三暑假的暑期实习是拿Return Offer的最佳路径。投行、咨询和大厂的Summer Intern通常需要提前一年（大二暑假到大三上学期）就开始投递。时间线比国内早半年！"
            },
            "senior": {
                "name": "Senior（大四）",
                "stage": "Full-time求职/申研/申博",
                "key_months": "大四上学期9-12月 Full-time秋招（比国内早），春季补录",
                "advice": "如果有Return Offer，大四会轻松很多。如果没有，秋招是最后一个大的招聘窗口。同时申请研究生的同学也要做好两手准备。"
            }
        }
    },
    "overseas_master": {
        "name": "海外硕士（海硕）",
        "duration": 1,
        "grades": {
            "one_year": {
                "name": "一年制（英/港/新等）",
                "stage": "入学即秋招，节奏极快，无试错空间",
                "key_months": "9月入学 → 同步秋招投递 → 次年1-3月春招补录 → 6-8月毕业入职",
                "advice": "一年制硕士最大的挑战是时间！入学第一天就是秋招第一天。建议入学前（暑假）就准备好简历、开始刷题、了解目标公司和岗位。没有任何试错空间。"
            },
            "one_half_year": {
                "name": "1.5年制（部分美/澳）",
                "stage": "中间有一个暑假，可以争取实习",
                "key_months": "第一年9月入学 → 次年3-5月投暑期实习 → 暑假实习 → 次年9月秋招 Full-time",
                "advice": "比一年制多了一个暑假窗口。如果能在暑假拿到一份高质量实习，对后续秋招帮助巨大。建议入学后立即开始准备暑期实习投递。"
            },
            "two_year": {
                "name": "两年制（美/加为主）",
                "stage": "第一年暑期实习，第二年 Full-time",
                "key_months": "第一年9-11月投次年Summer Intern → 暑假实习 → 第二年9月秋招 Full-time",
                "advice": "时间相对充裕。第一年重点是拿下高质量的暑期实习，第二年利用实习经历在秋招中获取更好的Full-time Offer。"
            }
        }
    },
    "overseas_phd": {
        "name": "海外博士（海博）",
        "duration": 5,
        "grades": {
            "general": {
                "name": "海博全阶段",
                "stage": "5-6年制为主，Research Intern通常在暑假",
                "key_months": "OPT/CPT签证需关注，H1B抽签、回国vs留美决策",
                "advice": "海博除了学术积累外，还要关注身份问题（OPT/CPT/H1B）。建议博三开始思考回国还是留美，两条路径的准备策略差异很大。工业界Research Intern是很好的试水方式。"
            }
        }
    }
}

# ============ 第三维：当前阶段（动态核心维度） ============
STAGES = {
    "S1": {
        "id": "S1",
        "name": "刚入学 / 迷茫探索期",
        "emoji": "🌱",
        "description": "对行业无概念，不知道专业出路，方向感 ≈ 0",
        "core_needs": ["行业认知扫盲", "专业出路地图", "兴趣挖掘"],
        "key_actions": [
            "完成专业出路探索问卷",
            "浏览不同行业的真实工作日常",
            "尝试1-2个短期体验项目",
            "加入1-2个感兴趣的社团"
        ],
        "ai_persona": "你是一位温暖耐心的学长/学姐，专门帮助刚入学的大一新生打开职业视野。你的语气要像朋友聊天一样轻松自然，多用鼓励的话语，少用专业术语。目标是帮TA建立对未来的好奇心和初步认知。"
    },
    "S2": {
        "id": "S2",
        "name": "专业积累期 / 方向模糊期",
        "emoji": "📚",
        "description": "知道一些方向但不确定选哪个，开始积累但缺乏规划",
        "core_needs": ["技能差距分析", "学习路径推荐", "项目/竞赛引导"],
        "key_actions": [
            "完成技能自评，找到与目标岗位的差距",
            "制定个性化学习路径",
            "参与1个学科竞赛或创新项目",
            "尝试投递中小公司的日常实习"
        ],
        "ai_persona": "你是一位有经验的导师/教练，帮助大二、研一的同学规划技能积累路径。你需要帮助TA识别当前能力与目标岗位的差距，给出具体可执行的学习建议。语气要专业但不生硬，像一位有经验的学长。"
    },
    "S3": {
        "id": "S3",
        "name": "实习准备期 / 简历打磨期",
        "emoji": "📝",
        "description": "明确想尝试的方向，开始准备简历和面试",
        "core_needs": ["简历优化", "模拟面试", "岗位JD拆解", "投递策略"],
        "key_actions": [
            "完成简历深度诊断和优化",
            "进行3-5次模拟面试练习",
            "拆解目标岗位JD，对标能力要求",
            "制定投递时间表和优先级"
        ],
        "ai_persona": "你是一位资深的求职辅导老师，擅长简历修改和面试辅导。你需要帮TA精修简历，分析JD，模拟面试。语气要专业、直接、有建设性，不吝啬指出问题但绝不能打击信心。"
    },
    "S4": {
        "id": "S4",
        "name": "实习中 / 经验验证期",
        "emoji": "💼",
        "description": "正在实习，验证「这个方向是否适合我」",
        "core_needs": ["经验沉淀方法", "转正策略", "职场软技能"],
        "key_actions": [
            "每日/每周实习复盘记录",
            "评估「这份工作是否适合我」",
            "了解转正流程和关键节点",
            "建立职场人脉和导师关系"
        ],
        "ai_persona": "你是一位职场过来人，理解实习生的处境和困惑。你需要帮TA分析当前实习体验，判断行业是否匹配，给出转正和下一段实习的策略建议。语气要共情、务实。"
    },
    "S5": {
        "id": "S5",
        "name": "正式求职期",
        "emoji": "🎯",
        "description": "秋招/春招窗口期，高强度投递和面试",
        "core_needs": ["投递节奏管理", "笔试刷题", "面试复盘", "Offer比较"],
        "key_actions": [
            "建立投递追踪表，管理多个流程",
            "每日/每周面试复盘和总结",
            "笔试高频题针对性练习",
            "多Offer比较决策框架"
        ],
        "ai_persona": "你是一位经验丰富的校招面试官，了解各大公司的面试标准和流程。你需要帮TA复盘面试，分析Offer优劣，管理求职节奏。语气要冷静、理性、有数据支撑。"
    },
    "S6": {
        "id": "S6",
        "name": "已上岸 / Landing衔接期",
        "emoji": "🎉",
        "description": "已拿到Offer，等待入职",
        "core_needs": ["入职准备", "技能预修", "职场身份转换", "校友连接"],
        "key_actions": [
            "了解入职公司的文化和团队",
            "预习入职后需要的技术/技能",
            "调整心态：从学生到职场人",
            "连接同公司的学长学姐"
        ],
        "ai_persona": "你是一位贴心的职场前辈，经历过从学生到职场人的转变。你需要帮TA做好入职前的心理和技术准备，缓解「空窗焦虑」。语气要温暖、鼓励，像一位过来人朋友。"
    },
    "S7": {
        "id": "S7",
        "name": "深造准备期",
        "emoji": "🎓",
        "description": "准备考研/保研/申博/留学申请",
        "core_needs": ["选校定位", "推荐信", "研究计划", "备选求职方案"],
        "key_actions": [
            "完成选校定位和目标院校分析",
            "准备推荐信和研究计划",
            "制定备考/申请时间表",
            "准备Plan B求职方案"
        ],
        "ai_persona": "你是一位有经验的升学顾问，熟悉考研、保研和留学申请的流程。你需要帮TA制定申请策略，但同时提醒做好Plan B（如果申请失利后的求职准备）。语气要务实、有策略性。"
    }
}

# ============ 行业定义 ============
INDUSTRIES = [
    {"id": "internet", "name": "互联网/科技", "icon": "💻"},
    {"id": "finance", "name": "金融", "icon": "💰"},
    {"id": "consulting", "name": "咨询", "icon": "📊"},
    {"id": "manufacturing", "name": "制造/工业", "icon": "🏭"},
    {"id": "fmcg", "name": "快消/零售", "icon": "🛒"},
    {"id": "healthcare", "name": "医疗/健康", "icon": "🏥"},
    {"id": "education", "name": "教育", "icon": "📖"},
    {"id": "energy", "name": "能源/环保", "icon": "⚡"},
    {"id": "law", "name": "法律", "icon": "⚖️"},
    {"id": "media", "name": "传媒/广告", "icon": "📺"},
    {"id": "gaming", "name": "游戏", "icon": "🎮"},
    {"id": "ai", "name": "人工智能", "icon": "🤖"},
    {"id": "semiconductor", "name": "芯片/半导体", "icon": "🔬"},
    {"id": "auto", "name": "汽车/新能源", "icon": "🚗"},
    {"id": "gov", "name": "公务员/事业单位", "icon": "🏛️"},
]

# ============ 阶段内容推荐模板 ============
STAGE_CONTENT_TEMPLATES = {
    "S1": {
        "title": "从这里开始探索",
        "sections": [
            {"type": "industry_intro", "title": "行业初印象", "desc": "快速浏览不同行业的真实工作日常"},
            {"type": "major_map", "title": "我的专业能做什么？", "desc": "看看同专业学长学姐都去了哪里"},
            {"type": "career_quiz", "title": "职业兴趣测评", "desc": "通过测评了解你可能的职业方向"},
            {"type": "experience", "title": "短期体验推荐", "desc": "适合大一新生的项目、比赛、活动"}
        ]
    },
    "S2": {
        "title": "能力积累规划",
        "sections": [
            {"type": "skill_gap", "title": "能力差距分析", "desc": "对标目标岗位，看看还差什么"},
            {"type": "learning_path", "title": "学习路径推荐", "desc": "从入门到进阶的系统学习路线"},
            {"type": "project_guide", "title": "项目/竞赛指南", "desc": "值得参与的学科竞赛和创新项目"},
            {"type": "early_intern", "title": "早期实习机会", "desc": "适合大二同学的日常实习信息"}
        ]
    },
    "S3": {
        "title": "全力冲刺实习",
        "sections": [
            {"type": "resume_review", "title": "简历深度诊断", "desc": "AI + 人工的简历优化服务"},
            {"type": "mock_interview", "title": "模拟面试", "desc": "技术面、行为面、群面全覆盖"},
            {"type": "jd_analysis", "title": "JD拆解", "desc": "手把手教你读懂岗位要求"},
            {"type": "timeline", "title": "投递时间表", "desc": "各公司暑期实习投递截止日历"}
        ]
    },
    "S4": {
        "title": "实习价值最大化",
        "sections": [
            {"type": "reflection", "title": "实习复盘工具", "desc": "每天5分钟，记录今日收获与困惑"},
            {"type": "return_offer", "title": "转正攻略", "desc": "了解转正流程、关键节点、述职技巧"},
            {"type": "soft_skill", "title": "职场软技能", "desc": "向上管理、跨部门沟通、时间管理"},
            {"type": "next_step", "title": "下一段规划", "desc": "评估当前方向是否适合，制定后续计划"}
        ]
    },
    "S5": {
        "title": "求职冲刺工具包",
        "sections": [
            {"type": "tracker", "title": "投递追踪表", "desc": "管理所有投递进度，不错过任何一个"},
            {"type": "interview_review", "title": "面试复盘模板", "desc": "每场面试后结构化复盘"},
            {"type": "offer_compare", "title": "Offer比较框架", "desc": "多维度评估不同Offer"},
            {"type": "mental_health", "title": "求职心理调适", "desc": "应对焦虑、拒绝和压力的方法"}
        ]
    },
    "S6": {
        "title": "从容开启职场",
        "sections": [
            {"type": "company_preview", "title": "公司/团队了解", "desc": "深入了解入职公司的文化和业务"},
            {"type": "skill_prep", "title": "技能预修", "desc": "入职前可以提前准备的技能"},
            {"type": "identity_shift", "title": "身份转换课", "desc": "从学生思维到职场思维的转变"},
            {"type": "alumni_connect", "title": "校友连接", "desc": "找到同公司的学长学姐"}
        ]
    },
    "S7": {
        "title": "深造就绪",
        "sections": [
            {"type": "school_selection", "title": "选校定位", "desc": "基于背景的精准选校策略"},
            {"type": "application_docs", "title": "申请材料准备", "desc": "PS/SOP/CV/推荐信指南"},
            {"type": "exam_prep", "title": "考试备考", "desc": "考研/保研/雅思/托福/GRE备考方案"},
            {"type": "plan_b", "title": "Plan B方案", "desc": "如果申请失利，求职怎么做"}
        ]
    }
}


# ============ 成长路线图模板 ============
# ⚠️ 仅作参考：以下路线图由AI根据通用经验生成，可能存在常识性错误或过时信息，请结合实际情况判断
ROADMAP_TEMPLATES = {
    "general": {
        "name": "通用成长路线",
        "stages": [
            {
                "name": "自我认知",
                "icon": "🔍",
                "milestones": [
                    {"name": "完成霍兰德测评", "verification": "完成全部题目并获得结果", "hours": 0.5},
                    {"name": "梳理个人优势清单", "verification": "列出至少5项个人优势和对应事例", "hours": 1},
                    {"name": "明确职业兴趣方向", "verification": "确定2-3个感兴趣的行业/岗位", "hours": 1},
                ]
            },
            {
                "name": "技能积累",
                "icon": "📚",
                "milestones": [
                    {"name": "学习岗位核心技能", "verification": "完成至少1门相关课程", "hours": 20},
                    {"name": "完成一个实战项目", "verification": "有可展示的项目成果", "hours": 30},
                    {"name": "获得相关证书", "verification": "获得1个行业认可的证书", "hours": 10},
                ]
            },
            {
                "name": "实践检验",
                "icon": "🎯",
                "milestones": [
                    {"name": "投递第一份简历", "verification": "完成简历并投递", "hours": 2},
                    {"name": "完成第一次面试", "verification": "参加面试并记录复盘", "hours": 1},
                    {"name": "获得第一个Offer", "verification": "收到正式录用通知", "hours": 0},
                ]
            },
            {
                "name": "复盘迭代",
                "icon": "🔄",
                "milestones": [
                    {"name": "总结求职经验", "verification": "写一份求职复盘文档", "hours": 2},
                    {"name": "更新个人发展规划", "verification": "基于复盘结果调整目标", "hours": 1},
                ]
            },
        ]
    },
    "tech": {
        "name": "技术岗路线",
        "stages": [
            {
                "name": "基础夯实",
                "icon": "💻",
                "milestones": [
                    {"name": "掌握一门编程语言", "verification": "能独立完成小项目", "hours": 40},
                    {"name": "学习数据结构与算法", "verification": "完成LeetCode 50题", "hours": 30},
                    {"name": "理解计算机网络基础", "verification": "能解释HTTP/TCP等核心概念", "hours": 15},
                ]
            },
            {
                "name": "项目实战",
                "icon": "🚀",
                "milestones": [
                    {"name": "完成个人项目", "verification": "有GitHub仓库和线上Demo", "hours": 40},
                    {"name": "参与开源项目", "verification": "提交至少1个PR被合并", "hours": 20},
                    {"name": "写技术博客", "verification": "发布3篇技术文章", "hours": 10},
                ]
            },
            {
                "name": "求职冲刺",
                "icon": "🎯",
                "milestones": [
                    {"name": "准备技术面试", "verification": "完成LeetCode 100题", "hours": 50},
                    {"name": "模拟面试", "verification": "完成3次模拟面试", "hours": 3},
                    {"name": "投递目标公司", "verification": "投递10家目标公司", "hours": 5},
                ]
            },
        ]
    },
    "product": {
        "name": "产品岗路线",
        "stages": [
            {
                "name": "产品思维",
                "icon": "💡",
                "milestones": [
                    {"name": "阅读产品经典书籍", "verification": "读完《启示录》《俞军产品方法论》等", "hours": 20},
                    {"name": "完成产品分析报告", "verification": "写3份App产品分析报告", "hours": 15},
                    {"name": "学习数据分析", "verification": "掌握SQL和基本数据分析方法", "hours": 20},
                ]
            },
            {
                "name": "实战练习",
                "icon": "📝",
                "milestones": [
                    {"name": "完成产品设计项目", "verification": "输出完整的PRD文档", "hours": 20},
                    {"name": "参与产品比赛", "verification": "参加至少1次产品比赛", "hours": 30},
                    {"name": "实习/项目经历", "verification": "获得产品相关实习或项目经验", "hours": 80},
                ]
            },
            {
                "name": "求职准备",
                "icon": "🎤",
                "milestones": [
                    {"name": "准备产品面试题", "verification": "整理50道常见产品面试题的回答", "hours": 15},
                    {"name": "模拟群面", "verification": "参加3次模拟群面", "hours": 6},
                    {"name": "建立行业认知", "verification": "能分析目标公司的产品和战略", "hours": 10},
                ]
            },
        ]
    },
    "design": {
        "name": "设计岗路线",
        "stages": [
            {"name": "基础功底", "icon": "🎨", "milestones": [
                {"name": "掌握设计工具", "verification": "熟练使用Figma/Sketch/PS", "hours": 30},
                {"name": "学习设计理论", "verification": "理解色彩/排版/构图基本原则", "hours": 20},
                {"name": "临摹优秀作品", "verification": "完成10份高质量临摹", "hours": 30},
            ]},
            {"name": "作品积累", "icon": "🖼️", "milestones": [
                {"name": "完成作品集网站", "verification": "上线个人设计作品集", "hours": 40},
                {"name": "参与实际项目", "verification": "完成至少2个真实设计项目", "hours": 60},
                {"name": "发布设计文章", "verification": "在设计社区发布3篇总结", "hours": 10},
            ]},
            {"name": "求职冲刺", "icon": "📱", "milestones": [
                {"name": "优化作品集", "verification": "针对目标公司优化作品集", "hours": 20},
                {"name": "准备设计面试", "verification": "完成设计挑战题5道", "hours": 15},
                {"name": "投递目标公司", "verification": "投递10家目标公司", "hours": 5},
            ]},
        ]
    },
    "finance": {
        "name": "金融岗路线",
        "stages": [
            {"name": "知识储备", "icon": "📈", "milestones": [
                {"name": "掌握财务分析", "verification": "能独立完成三张报表分析", "hours": 30},
                {"name": "学习估值模型", "verification": "掌握DCF/可比公司等估值方法", "hours": 25},
                {"name": "考取从业资格", "verification": "通过证券/基金从业资格考试", "hours": 40},
            ]},
            {"name": "实习积累", "icon": "💼", "milestones": [
                {"name": "完成金融实习", "verification": "获得券商/基金/银行实习经历", "hours": 200},
                {"name": "撰写研究报告", "verification": "独立完成1份行业或公司研究报告", "hours": 20},
                {"name": "建立金融人脉", "verification": "参加3次行业交流活动", "hours": 10},
            ]},
            {"name": "求职冲刺", "icon": "🎯", "milestones": [
                {"name": "准备技术面试", "verification": "复习财务/估值/市场知识", "hours": 30},
                {"name": "模拟面试", "verification": "完成5次模拟面试", "hours": 5},
                {"name": "投递目标机构", "verification": "投递15家目标公司", "hours": 8},
            ]},
        ]
    },
    "operation": {
        "name": "运营岗路线",
        "stages": [
            {"name": "基础能力", "icon": "📊", "milestones": [
                {"name": "学习数据分析", "verification": "掌握Excel/SQL基本操作", "hours": 20},
                {"name": "了解运营框架", "verification": "学习AARRR/用户生命周期等模型", "hours": 10},
                {"name": "拆解经典案例", "verification": "分析5个知名运营案例", "hours": 15},
            ]},
            {"name": "实战经验", "icon": "🚀", "milestones": [
                {"name": "运营个人账号", "verification": "从0做到1000粉丝", "hours": 50},
                {"name": "参与活动策划", "verification": "策划并执行1次线上/线下活动", "hours": 20},
                {"name": "完成运营实习", "verification": "获得运营相关实习经历", "hours": 160},
            ]},
            {"name": "求职准备", "icon": "🎯", "milestones": [
                {"name": "准备作品集", "verification": "整理运营案例和数据成果", "hours": 10},
                {"name": "模拟面试", "verification": "准备常见运营面试题", "hours": 8},
                {"name": "投递目标公司", "verification": "投递10家目标公司", "hours": 5},
            ]},
        ]
    },
    "consulting": {
        "name": "咨询岗路线",
        "stages": [
            {"name": "思维训练", "icon": "🧠", "milestones": [
                {"name": "练习Case面试", "verification": "完成30个Case练习", "hours": 60},
                {"name": "学习商业框架", "verification": "掌握波特五力/SWOT/BCG等", "hours": 15},
                {"name": "提升Excel/PPT", "verification": "能快速产出专业图表", "hours": 20},
            ]},
            {"name": "经验积累", "icon": "📋", "milestones": [
                {"name": "参加商赛", "verification": "参加至少1次商业案例比赛", "hours": 30},
                {"name": "完成咨询实习", "verification": "获得咨询/战略相关实习", "hours": 160},
                {"name": "建立行业认知", "verification": "深入了解2-3个行业", "hours": 20},
            ]},
            {"name": "求职冲刺", "icon": "🎤", "milestones": [
                {"name": "模拟Case面试", "verification": "完成10次模拟Case面试", "hours": 15},
                {"name": "准备Fit面试", "verification": "准备好行为面试故事", "hours": 8},
                {"name": "投递目标公司", "verification": "投递MBB/Tier2等目标公司", "hours": 5},
            ]},
        ]
    },
    "ai_ml": {
        "name": "AI/算法岗路线",
        "stages": [
            {"name": "数学基础", "icon": "📐", "milestones": [
                {"name": "复习线性代数", "verification": "掌握矩阵运算/特征值/SVD", "hours": 30},
                {"name": "复习概率统计", "verification": "掌握贝叶斯/假设检验/分布", "hours": 25},
                {"name": "学习最优化方法", "verification": "理解梯度下降/凸优化", "hours": 20},
            ]},
            {"name": "算法实战", "icon": "🤖", "milestones": [
                {"name": "掌握经典ML算法", "verification": "能手写LR/SVM/决策树/随机森林", "hours": 40},
                {"name": "学习深度学习", "verification": "掌握CNN/RNN/Transformer原理", "hours": 50},
                {"name": "完成Kaggle竞赛", "verification": "至少参加1次并进入前50%", "hours": 60},
            ]},
            {"name": "求职冲刺", "icon": "🎯", "milestones": [
                {"name": "刷LeetCode", "verification": "完成200题以上", "hours": 80},
                {"name": "准备ML八股文", "verification": "整理常见面试题100道", "hours": 20},
                {"name": "投递目标公司", "verification": "投递10家AI/算法岗位", "hours": 5},
            ]},
        ]
    },
    "embedded": {
        "name": "嵌入式/硬件岗路线",
        "stages": [
            {"name": "基础夯实", "icon": "🔌", "milestones": [
                {"name": "掌握C/C++", "verification": "能独立完成嵌入式项目", "hours": 50},
                {"name": "学习微机原理", "verification": "理解ARM/Cortex-M架构", "hours": 30},
                {"name": "掌握RTOS", "verification": "能使用FreeRTOS/RT-Thread", "hours": 25},
            ]},
            {"name": "项目实战", "icon": "🛠️", "milestones": [
                {"name": "完成STM32项目", "verification": "独立完成传感器+通信+控制项目", "hours": 60},
                {"name": "学习Linux驱动", "verification": "完成字符设备驱动开发", "hours": 40},
                {"name": "参加电子竞赛", "verification": "参加电赛/智能车等比赛", "hours": 80},
            ]},
            {"name": "求职冲刺", "icon": "🎯", "milestones": [
                {"name": "复习模电数电", "verification": "能分析常见电路", "hours": 20},
                {"name": "准备技术面试", "verification": "整理C/OS/驱动面试题", "hours": 15},
                {"name": "投递目标公司", "verification": "投递10家硬件/嵌入式公司", "hours": 5},
            ]},
        ]
    },
    "civil_mechanical": {
        "name": "土木/机械岗路线",
        "stages": [
            {"name": "专业基础", "icon": "🏗️", "milestones": [
                {"name": "掌握专业软件", "verification": "熟练使用AutoCAD/SolidWorks/ANSYS", "hours": 60},
                {"name": "学习行业规范", "verification": "熟悉相关国家标准", "hours": 30},
                {"name": "了解BIM技术", "verification": "完成BIM基础建模", "hours": 25},
            ]},
            {"name": "实践积累", "icon": "📐", "milestones": [
                {"name": "完成课程设计", "verification": "独立完成结构/机械设计项目", "hours": 50},
                {"name": "参加专业竞赛", "verification": "参加结构设计/成图等竞赛", "hours": 40},
                {"name": "完成工地/工厂实习", "verification": "获得现场实践经验", "hours": 160},
            ]},
            {"name": "求职冲刺", "icon": "🎯", "milestones": [
                {"name": "考取专业证书", "verification": "通过二建/一建/注册工程师基础考试", "hours": 60},
                {"name": "准备面试", "verification": "整理专业知识和项目经验", "hours": 15},
                {"name": "投递目标公司", "verification": "投递10家设计院/工程公司", "hours": 5},
            ]},
        ]
    },
    "medical_bio": {
        "name": "医药/生科岗路线",
        "stages": [
            {"name": "专业积累", "icon": "🧬", "milestones": [
                {"name": "掌握实验技能", "verification": "熟练操作PCR/Western Blot等", "hours": 80},
                {"name": "阅读文献", "verification": "每周精读2篇英文文献", "hours": 60},
                {"name": "学习生信分析", "verification": "掌握R/Python基础数据分析", "hours": 30},
            ]},
            {"name": "科研实战", "icon": "🔬", "milestones": [
                {"name": "完成课题研究", "verification": "独立完成1个完整课题", "hours": 200},
                {"name": "发表论文", "verification": "以第一作者投稿SCI", "hours": 100},
                {"name": "参加学术会议", "verification": "至少参加1次并做报告", "hours": 20},
            ]},
            {"name": "求职冲刺", "icon": "🎯", "milestones": [
                {"name": "准备简历", "verification": "突出科研能力和实验技能", "hours": 8},
                {"name": "了解行业去向", "verification": "调研药企/CRO/IVD等方向", "hours": 10},
                {"name": "投递目标公司", "verification": "投递10家药企/生物公司", "hours": 5},
            ]},
        ]
    },
}


# ============ 焦虑急救包 ============
ANXIETY_FLOW = {
    "step1": {"title": "识别情绪", "duration": "30秒"},
    "step2": {"title": "认知重构", "duration": "1分钟"},
    "step3": {
        "title": "微行动",
        "duration": "2分钟",
        "micro_actions": [
            "现在放下手机，做3次深呼吸",
            "站起来走一圈，活动身体",
            "写下三个你已经做到的事，无论大小",
            "听一首让你平静的歌",
            "对自己说：我在路上，慢慢来",
            "喝一杯水，补充能量",
            "做一次肩颈拉伸",
            "看看窗外的天空",
        ]
    },
}

EMOTION_KEYWORDS = {
    "anxiety": ["焦虑", "紧张", "担心", "不安", "压力", "喘不过气", "心慌"],
    "rejection": ["被拒", "拒了", "没过", "失败了", "挂了", "凉了", "没戏了"],
    "self_doubt": ["我不行", "不够好", "不如别人", "配不上", "没能力", "太差了", "自卑"],
    "confusion": ["迷茫", "不知道", "不确定", "看不清", "没有方向", "不知道该做什么"],
    "exhaustion": ["累", "疲惫", "倦怠", "没力气", "精力耗尽", "筋疲力尽", "不想动了"],
}
