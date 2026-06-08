"""简历与面试服务 —— 参考 get-job skill 的翻译+审计方法论

核心原则：
- 翻译 ≠ 编造。只改表达方式，不改事实。
- 每个"可迁移能力"对应一件真做过的事。
- 诚实是底线：讲不清的数字模糊化，不要硬编。
"""

import json
from services.ai_service import chat_non_stream


class ResumeWriter:
    """将经历改写为简历条目 + 完整简历"""

    @staticmethod
    async def rewrite_for_position(
        experience_text: str,
        target_position: str,
        position_keywords: list[str],
    ) -> dict:
        """将简历原文或经历描述改写为面向目标岗位的简历

        输入：用户的原始简历/经历 + 目标岗位 + 关键词
        输出：改写后的 bullet 列表 + 技能 + 量化 + 迁移说明
        """
        prompt = f"""你是简历优化师。你的任务是把用户的真实经历"翻译"成目标岗位的语言。

## 核心原则（不可违反）
1. 翻译 ≠ 编造。只改表达方式，不改事实。
2. 每个技能/成果都要有真实经历对应。
3. 讲不清来源的数字改成模糊表述（如"显著提升""约X%"），不要硬编。
4. 学历、职位名、时间等硬信息一个字不能动。

## 目标岗位
{target_position if target_position else '通用岗位'}

## 岗位关键词
{', '.join(position_keywords) if position_keywords else '通用能力'}

## 用户简历/经历原文
{experience_text[:3000]}

## 输出要求
请输出JSON：
{{
    "summary": "2-3句概述，突出与目标岗位最相关的经历和能力",
    "bullets": ["改写后的简历条目（每条含具体行动+可验证成果，每条约30字）", ...],
    "skills": ["从经历中提取的技能（3-5个）", ...],
    "quantified": ["量化成果（如实提取，没有就写'待补充'）", ...],
    "transferable_note": "如果经历与目标岗位不完全对口，说明哪些能力可迁移（对口则写'直接匹配'）",
    "improvement_tips": ["简历还可以优化的3个方向", ...]
}}"""

        try:
            result = await chat_non_stream(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="你是简历优化师。只输出JSON，确保每个claims都有真实经历支撑。",
                max_tokens=1200,
            )
            cleaned = result.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(cleaned)
        except Exception:
            return {
                "summary": "简历优化中...",
                "bullets": [experience_text[:200]],
                "skills": [],
                "quantified": [],
                "transferable_note": "",
                "improvement_tips": [],
            }

    @staticmethod
    async def generate_resume_summary(
        experiences: list[dict],
        target_position: str,
        name: str = "",
    ) -> dict:
        """从多段经历生成完整简历（含优势+缺口分析）"""
        all_text = ""
        for exp in experiences:
            title = exp.get("title", "")
            bullets = exp.get("bullets", [])
            all_text += f"【{title}】\n" + "\n".join(bullets) + "\n\n"

        prompt = f"""你是简历架构师。根据以下经历素材，生成一份面向「{target_position}」的完整简历。

## 经历素材
{all_text[:3000]}

## 输出JSON
{{
    "summary": "简历顶部概述，2-3句话",
    "core_experiences": [
        {{"title": "经历名称", "bullets": ["简历条目"], "skills_shown": ["体现的技能"]}}
    ],
    "key_skills": ["核心技能1", "核心技能2", ...],
    "strengths": ["你的3个核心优势"],
    "gaps": ["与目标岗位相比还需要补强的2-3个方向"]
}}"""

        try:
            result = await chat_non_stream(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="你是简历架构师。只输出JSON。",
                max_tokens=1200,
            )
            cleaned = result.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(cleaned)
        except Exception:
            return {
                "summary": f"面向{target_position}岗位的求职者。",
                "core_experiences": experiences[:3],
                "key_skills": [],
                "strengths": [],
                "gaps": [],
            }

    @staticmethod
    def build_checklist() -> list[dict]:
        """简历提交前自检清单"""
        return [
            {"check": "每段经历都有量化数据或具体成果", "why": "面试官看简历平均6秒，数字最抓眼球"},
            {"check": "和目标岗位无关的内容已删除或弱化", "why": "无关信息会稀释你的核心竞争力"},
            {"check": "没有编造的数据或经历", "why": "面试追问三层一定崩，诚实比完美重要"},
            {"check": "专业术语和岗位JD对齐", "why": "用对方熟悉的语言描述你的经历"},
            {"check": "学历/时间/职位名等硬信息核对无误", "why": "背调会核实，一个字不能差"},
        ]


class InterviewCoach:
    """面试准备：证据化审计 + 话术生成"""

    @staticmethod
    async def audit_experiences(experiences: list[dict]) -> list[dict]:
        """逐段审计经历的可追问性（证据化审计）"""
        audited = []
        for exp in experiences[:5]:
            title = exp.get("title", "经历")
            bullets = exp.get("bullets", [])

            prompt = f"""你是面试官。请审计以下经历在面试中的可追问性。

经历：{title}
内容：{' | '.join(bullets[:3])}

请评估：
1. 面试官最可能追问哪3个问题？
2. 哪些数字或结论需要提前准备好来源解释？
3. 整体风险等级：低（经得起追问）/ 中（部分细节需要补）/ 高（可能被问穿）

只输出JSON：
{{"questions": ["追问1", "追问2", "追问3"], "weak_spots": ["薄弱点"], "risk": "低|中|高", "advice": "准备建议（30字内）"}}"""

            try:
                result = await chat_non_stream(
                    messages=[{"role": "user", "content": prompt}],
                    system_prompt="你是面试官。只输出JSON。",
                    max_tokens=400,
                )
                cleaned = result.strip().removeprefix("```json").removesuffix("```").strip()
                audit = json.loads(cleaned)
                audit["title"] = title
                audited.append(audit)
            except Exception:
                audited.append({
                    "title": title,
                    "questions": ["请详细说说你在这段经历中的具体角色"],
                    "weak_spots": [],
                    "risk": "中",
                    "advice": "提前准备好具体数据和决策过程",
                })

        return audited

    @staticmethod
    async def craft_self_intro(
        name: str,
        target_position: str,
        best_experience: str,
        key_skills: list[str],
    ) -> str:
        """生成30秒自我介绍（自然口语版）"""
        prompt = f"""请为以下求职者写一段30秒的面试自我介绍。

求职者：{name}
目标岗位：{target_position}
最有代表性的经历：{best_experience}
核心能力：{', '.join(key_skills[:3]) if key_skills else '通用能力'}

要求：
- 约80-120字，30秒能说完
- 像真人说话，不是背稿
- 开头就亮出最强钩子（经历+成果）
- 每个字都能被追问而不崩

只输出自我介绍文本。"""

        try:
            result = await chat_non_stream(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="你是面试教练。输出自然口语化的自我介绍。",
                max_tokens=300,
            )
            return result.strip()
        except Exception:
            return f"面试官好，我是{name}，目标是{target_position}。我最有代表性的经历是{best_experience}。"

    @staticmethod
    async def generate_interview_questions(
        jd_text: str,
        target_position: str,
        experiences: list[dict],
    ) -> list[dict]:
        """根据JD和简历生成可能的面试问题（参考get-job skill的建题库）"""
        exp_text = ""
        for e in experiences[:3]:
            exp_text += f"- {e.get('title', '')}: {', '.join(e.get('bullets', [])[:2])}\n"

        prompt = f"""你是面试官。请根据以下JD和求职者经历，生成面试可能问的问题。

## 目标岗位
{target_position}

## JD内容
{jd_text[:1500]}

## 求职者经历
{exp_text}

请按频率分级输出：
- 🔴必考：JD明确要求、一定会问的（3-4题）
- 🟡高频：大概率会问的（3-4题）
- 🟢可能：根据经历延伸的（2-3题）

每道题附带回答提示。

输出JSON：
[
    {{"level": "red", "question": "问题", "tip": "回答提示（30字）"}},
    ...
]"""

        try:
            result = await chat_non_stream(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="你是面试官。只输出JSON数组。",
                max_tokens=1000,
            )
            cleaned = result.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(cleaned)
        except Exception:
            return [
                {"level": "red", "question": f"你为什么想投{target_position}？", "tip": "关联你的经历和能力"},
                {"level": "red", "question": "请简单介绍一下你自己", "tip": "用30秒版本，突出最强钩子"},
                {"level": "yellow", "question": "说说你最有代表性的项目", "tip": "用STAR结构"},
                {"level": "yellow", "question": "你的职业规划是什么？", "tip": "展示长期兴趣"},
            ]

    @staticmethod
    async def build_interview_kit(
        experiences: list[dict],
        target_position: str,
        name: str = "",
        jd_text: str = "",
    ) -> dict:
        """一站式面试准备包"""
        # 1. 经历审计
        audit = await InterviewCoach.audit_experiences(experiences)

        # 2. 自我介绍
        best_exp = ""
        best_skills = []
        if experiences:
            best_exp = experiences[0].get("title", "")
            best_skills = experiences[0].get("skills_shown", [])

        self_intro = await InterviewCoach.craft_self_intro(
            name=name,
            target_position=target_position,
            best_experience=best_exp,
            key_skills=best_skills,
        )

        # 3. 常见问题
        common_questions = [
            {"question": "请简单介绍一下你自己", "tip": "用上面生成的自我介绍，30秒版本"},
            {"question": "说说你最有代表性的一个项目/经历", "tip": "按STAR结构讲"},
            {"question": f"你为什么想投{target_position}这个岗位？", "tip": "关联经历和能力说明匹配点"},
            {"question": "你的职业规划是什么？", "tip": "展示长期兴趣"},
        ]

        # 4. 根据JD生成针对性问题
        if jd_text:
            jd_questions = await InterviewCoach.generate_interview_questions(
                jd_text, target_position, experiences
            )
            common_questions.extend(jd_questions)

        # 从审计提取追问
        for item in audit[:3]:
            for q in item.get("questions", [])[:2]:
                common_questions.append({
                    "question": q,
                    "tip": f"针对「{item.get('title', '')}」经历",
                })

        # 5. 反问
        reverse_questions = [
            "这个岗位未来半年最重要要解决的问题是什么？",
            "团队目前的技术栈/工作方式是怎样的？",
            "这个岗位上做得好的同事通常具备什么特质？",
        ]

        return {
            "self_intro": self_intro,
            "experience_audit": audit,
            "common_questions": common_questions,
            "reverse_questions": reverse_questions,
            "prep_checklist": [
                "每段经历都能用STAR结构讲一遍",
                "简历上每个数字都能说清来源",
                "准备好2-3个反问",
                "了解目标公司的基本业务和产品",
            ],
        }
