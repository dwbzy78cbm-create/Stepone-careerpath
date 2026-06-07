"""AI 对话服务 —— V4.0 任务驱动版"""
import json
import httpx
from typing import AsyncGenerator, Optional

from config import AI_API_KEY, AI_API_BASE, AI_MODEL
from data_definitions import STAGES, MAJOR_CATEGORIES, EDUCATION_LEVELS


def build_system_prompt(
    stage_id: str,
    major_category: str = "",
    major_name: str = "",
    education_type: str = "",
    grade: str = "",
    target_industries: Optional[list] = None,
    nickname: str = "",
) -> str:
    """构建任务驱动型 System Prompt"""
    stage_info = STAGES.get(stage_id, STAGES["S1"])

    major_cat = MAJOR_CATEGORIES.get(major_category, {})
    major_cat_name = major_cat.get("name", "")
    career_dirs = major_cat.get("career_directions", [])

    edu_info = EDUCATION_LEVELS.get(education_type, {})
    edu_name = edu_info.get("name", "")
    grade_info = edu_info.get("grades", {}).get(grade, {})
    grade_name = grade_info.get("name", "")
    grade_stage = grade_info.get("stage", "")
    grade_months = grade_info.get("key_months", "")
    grade_advice = grade_info.get("advice", "")

    industries_str = ""
    if target_industries:
        industries_str = f"TA对以下行业感兴趣：{', '.join(target_industries)}。"

    prompt = f"""你是「一步」——一位 AI 求职成长陪伴助手。你的工作方式是苏格拉底式追问：通过提问引导用户自己发现答案。

## 你的角色
你是一位温暖但专业的导师。用户把经历和困惑告诉你，你通过层层深入的提问，帮TA自己看清自己的优势和方向。
语气：温暖、有洞察力、像一位真正关心TA成长的导师。用提问代替说教。

## 五层苏格拉底追问法（逐层深入）

你的核心方法是提问——不是直接给答案，而是通过问题引导用户自己发现答案。

**第1层·建立连接**：温暖问候 → 了解用户的基本情况 → 建立信任
**第2层·了解现状**：了解学业背景、求职状态、已有经历 → 建立用户画像
**第3层·挖掘线索**：在经历中寻找关键事件 → 追问细节 → 发现模式
**第4层·分析提炼**：帮用户看清核心竞争力 → 归纳总结 → 提出洞见
**第5层·行动规划**：给出具体建议 → 投递策略 → 补强方向

每层推进时，用自然的过渡语引导，不要生硬切换。

## 当前用户画像
- 称呼：{nickname or '同学'}
- 专业：{major_cat_name}{' - ' + major_name if major_name else ''}
- 学历：{edu_name} · {grade_name}
- 阶段：{grade_stage}（{grade_months}）
- 就业方向：{', '.join(career_dirs) if career_dirs else '待探索'}
{industries_str}

## 铁律
1. 每步完成后立刻推下一步，不等用户说"然后呢"
2. 推进时必须用推进语明确告知用户
3. 追问直接要数字，不要绕弯
4. 每次回复200字以内
5. 不说"很棒""加油"等废话
6. 不编造数据，不替用户做最终决定"""
    return prompt


async def chat_stream(
    messages: list[dict],
    system_prompt: str,
    max_tokens: int = 800,
) -> AsyncGenerator[str, None]:
    """流式 AI 对话（兼容 OpenAI API 格式）"""
    if not AI_API_KEY or AI_API_KEY == "your-api-key-here":
        yield "AI 服务尚未配置 API Key。请在后台设置 AI_API_KEY 环境变量。"
        return

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream(
                "POST",
                f"{AI_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": AI_MODEL,
                    "messages": full_messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "stream": True,
                },
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"AI 服务返回错误 (HTTP {response.status_code}): {error_text.decode()[:200]}"
                    return

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            yield "无法连接到 AI 服务，请检查 API 地址配置。"
        except Exception as e:
            yield f"AI 服务异常: {str(e)[:200]}"


async def chat_non_stream(
    messages: list[dict],
    system_prompt: str,
    max_tokens: int = 800,
) -> str:
    """非流式 AI 对话"""
    if not AI_API_KEY or AI_API_KEY == "your-api-key-here":
        return "AI 服务尚未配置 API Key。请在后台设置 AI_API_KEY 环境变量。"

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{AI_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": AI_MODEL,
                    "messages": full_messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            if response.status_code != 200:
                return f"AI 服务返回错误 (HTTP {response.status_code})"

            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "AI 返回了空内容")
        except Exception as e:
            return f"AI 服务异常: {str(e)[:200]}"


async def assess_dialogue_depth(
    messages: list[dict],
    user_profile: dict,
) -> dict:
    """AI 自动评估当前对话深度"""
    if not AI_API_KEY or AI_API_KEY == "your-api-key-here":
        return {"depth": "depth1", "reason": "API Key 未配置，默认 depth1"}

    # 构建对话摘要（最近10轮）
    recent = messages[-20:] if len(messages) > 20 else messages
    dialogue_text = ""
    for m in recent:
        role_label = "用户" if m.get("role") == "user" else "助手"
        content = m.get("content", "")[:200]
        dialogue_text += f"{role_label}: {content}\n"

    assess_prompt = f"""你是一位简历工作流分析专家。根据对话，判断当前处于简历加工流水线的哪个阶段。

五阶段定义（任务驱动）：
- depth1（描述经历）：用户正在把经历扔给AI，AI在接收和归类
- depth2（确认目标）：用户明确了求职岗位，AI在分析匹配度
- depth3（拆解经历）：AI在追问具体细节、数据、成果
- depth4（STAR转译）：AI正在用STAR法则改写经历为简历语言
- depth5（行动建议）：AI在给出投递策略、补强建议、面试预测

对话内容：
{dialogue_text}

用户画像：{json.dumps(user_profile, ensure_ascii=False)}

请只输出以下JSON格式（不要其他文字）：
{{"depth": "depth1|depth2|depth3|depth4|depth5", "reason": "简短判断理由（20字以内）"}}"""

    try:
        result = await chat_non_stream(
            messages=[{"role": "user", "content": assess_prompt}],
            system_prompt="你是简历工作流分析专家。只输出JSON。",
            max_tokens=200,
        )
        cleaned = result.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, Exception):
        # 降级：基于消息数量简单判断（任务驱动模式阈值更低）
        user_msgs = [m for m in messages if m.get("role") == "user"]
        count = len(user_msgs)
        if count >= 8:
            return {"depth": "depth4", "reason": "多轮追问细节"}
        elif count >= 5:
            return {"depth": "depth3", "reason": "正在拆解经历"}
        elif count >= 3:
            return {"depth": "depth2", "reason": "已确认目标"}
        else:
            return {"depth": "depth1", "reason": "接收经历中"}
