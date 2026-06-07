"""AI 对话 API —— 流式 + 非流式"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
import json
import asyncio
import os

from database import get_db
from models import User, Conversation, StageLog
from services.ai_service import chat_stream, chat_non_stream, build_system_prompt, assess_dialogue_depth
from services.conversation_depth import (
    DEPTH_DEFINITIONS,
    DEPTH_TRANSITIONS,
    NARRATIVE_ENTRY_CONDITIONS,
    NARRATIVE_TRIGGER_KEYWORDS,
)

router = APIRouter(prefix="/api/chat", tags=["AI对话"])


class ChatRequest(BaseModel):
    user_id: int
    message: str
    history_limit: int = 10


class ChatResponse(BaseModel):
    reply: str
    stage: str
    depth: Optional[str] = None
    show_narrative: bool = False


class StarRequest(BaseModel):
    user_id: int


class NarrativeRequest(BaseModel):
    user_id: int
    stage: str  # "story_mining" or "star_decomposition"
    content: Optional[str] = None
    clues: Optional[list[str]] = None


@router.post("/send")
async def send_message(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """发送消息，获取 AI 回复"""
    # 获取用户信息
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取最近历史对话
    history_result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == req.user_id)
        .order_by(desc(Conversation.created_at))
        .limit(req.history_limit * 2)
    )
    history = list(reversed(history_result.scalars().all()))

    messages = []
    for h in history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": req.message})

    # 构建系统提示词
    system_prompt = build_system_prompt(
        stage_id=user.current_stage,
        major_category=user.major_category,
        major_name=user.major_name,
        education_type=user.education_type,
        grade=user.grade,
        target_industries=user.target_industries,
        nickname=user.nickname,
    )

    # 保存用户消息
    user_msg = Conversation(
        user_id=user.id,
        role="user",
        content=req.message,
        context_stage=user.current_stage,
    )
    db.add(user_msg)

    # 获取 AI 回复
    reply = await chat_non_stream(messages, system_prompt)

    # 保存 AI 回复
    assistant_msg = Conversation(
        user_id=user.id,
        role="assistant",
        content=reply,
        context_stage=user.current_stage,
    )
    db.add(assistant_msg)
    await db.commit()

    # AI 自动评估对话深度
    depth_result = await assess_dialogue_depth(
        messages=messages,
        user_profile={
            "nickname": user.nickname,
            "stage": user.current_stage,
            "major": user.major_name,
            "grade": user.grade,
        }
    )

    # 记录深度变更
    if depth_result and depth_result.get("depth"):
        db.add(StageLog(
            user_id=user.id,
            from_stage="",
            to_stage=depth_result["depth"],
            reason=f"AI自动评估: {depth_result.get('reason', '对话深度更新')}"
        ))
        await db.commit()

    # 检查是否触发叙事入口
    show_narrative = False
    all_msgs = history + [user_msg, assistant_msg]
    user_msgs = [m for m in all_msgs if m.role == "user"]
    if depth_result and depth_result.get("depth"):
        depth_order = ["depth1", "depth2", "depth3", "depth4", "depth5"]
        current_idx = depth_order.index(depth_result["depth"]) if depth_result["depth"] in depth_order else 0
        required_idx = depth_order.index(NARRATIVE_ENTRY_CONDITIONS["min_depth"])
        if current_idx >= required_idx and len(user_msgs) >= NARRATIVE_ENTRY_CONDITIONS["min_user_messages"]:
            show_narrative = True

    return ChatResponse(
        reply=reply,
        stage=user.current_stage,
        depth=depth_result.get("depth") if depth_result else None,
        show_narrative=show_narrative,
    )


@router.post("/stream")
async def send_message_stream(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """流式发送消息"""
    # 获取用户信息
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取最近历史对话
    history_result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == req.user_id)
        .order_by(desc(Conversation.created_at))
        .limit(req.history_limit * 2)
    )
    history = list(reversed(history_result.scalars().all()))

    messages = []
    for h in history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": req.message})

    # 构建系统提示词
    system_prompt = build_system_prompt(
        stage_id=user.current_stage,
        major_category=user.major_category,
        major_name=user.major_name,
        education_type=user.education_type,
        grade=user.grade,
        target_industries=user.target_industries,
        nickname=user.nickname,
    )

    # 保存用户消息
    user_msg = Conversation(
        user_id=user.id,
        role="user",
        content=req.message,
        context_stage=user.current_stage,
    )
    db.add(user_msg)
    await db.commit()

    # 保存 context 供 generator 使用
    user_ctx = {
        "id": user.id,
        "nickname": user.nickname,
        "stage": user.current_stage,
        "major": user.major_name,
        "grade": user.grade,
    }
    history_count = len(history)

    async def generate():
        full_reply = ""
        async for chunk in chat_stream(messages, system_prompt):
            full_reply += chunk
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

        # 保存完整回复
        async with AsyncSession(db.bind) as save_session:
            save_session.add(Conversation(
                user_id=user_ctx["id"],
                role="assistant",
                content=full_reply,
                context_stage=user_ctx["stage"],
            ))
            await save_session.commit()

        # V3.5: 检查用户是否主动触发叙事
        user_msg_text = req.message
        show_narrative = False
        depth_id = None
        force_narrative = False

        # 关键词检测：用户主动要求叙事
        for keyword in NARRATIVE_TRIGGER_KEYWORDS:
            if keyword.lower() in user_msg_text.lower():
                force_narrative = True
                show_narrative = True
                depth_id = "depth3"  # 直接标记为线索挖掘阶段
                break

        if not force_narrative:
            # AI 自动评估对话深度
            all_messages = messages + [{"role": "assistant", "content": full_reply}]
            try:
                depth_result = await assess_dialogue_depth(
                    messages=all_messages,
                    user_profile=user_ctx,
                )
                if depth_result and depth_result.get("depth"):
                    depth_id = depth_result["depth"]
                    # 记录深度变更
                    async with AsyncSession(db.bind) as save_session:
                        save_session.add(StageLog(
                            user_id=user_ctx["id"],
                            from_stage="",
                            to_stage=depth_id,
                            reason=f"AI自动评估: {depth_result.get('reason', '对话深度更新')}"
                        ))
                        await save_session.commit()

                    # 检查叙事入口
                    depth_order = ["depth1", "depth2", "depth3", "depth4", "depth5"]
                    current_idx = depth_order.index(depth_id) if depth_id in depth_order else 0
                    required_idx = depth_order.index(NARRATIVE_ENTRY_CONDITIONS["min_depth"])
                    user_msg_count = len([m for m in all_messages if m.get("role") == "user"])
                    if current_idx >= required_idx and user_msg_count >= NARRATIVE_ENTRY_CONDITIONS["min_user_messages"]:
                        show_narrative = True
            except Exception as e:
                print(f"Depth assessment error: {e}")

        yield f"data: {json.dumps({'content': '', 'done': True, 'stage': user_ctx['stage'], 'depth': depth_id, 'show_narrative': show_narrative})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/history/{user_id}")
async def get_history(
    user_id: int,
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """获取对话历史"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.created_at))
        .limit(limit)
    )
    history = result.scalars().all()

    return {
        "messages": [
            {
                "id": h.id,
                "role": h.role,
                "content": h.content,
                "stage": h.context_stage,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in reversed(history)
        ],
        "total": len(history),
    }


@router.delete("/history/{user_id}")
async def clear_history(user_id: int, db: AsyncSession = Depends(get_db)):
    """清空对话历史"""
    result = await db.execute(
        select(Conversation).where(Conversation.user_id == user_id)
    )
    conversations = result.scalars().all()
    for c in conversations:
        await db.delete(c)
    await db.commit()

    return {"success": True, "message": "对话历史已清空"}


# ---------- STAR 分解 & 叙事重构 ----------

@router.post("/star")
async def star_decomposition(req: StarRequest, db: AsyncSession = Depends(get_db)):
    """基于对话历史进行 STAR 法则拆解"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取全部对话历史
    history_result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == req.user_id)
        .order_by(desc(Conversation.created_at))
        .limit(30)
    )
    history = list(reversed(history_result.scalars().all()))

    if len(history) < 4:
        return {"star_result": None, "message": "对话历史不足，请先多聊一会"}

    # 构建对话摘要
    dialogue_text = ""
    for h in history:
        role_label = "用户" if h.role == "user" else "AI"
        dialogue_text += f"{role_label}: {h.content[:300]}\n"

    # 使用 AI 进行 STAR 分解
    star_prompt = f"""你是一位职业规划专家。请根据以下对话历史，用 STAR 法则分析用户的关键经历。

对话历史：
{dialogue_text}

请输出以下格式的 JSON（只输出 JSON，不要其他文字）：
{{
    "experiences": [
        {{
            "title": "经历名称（简短）",
            "situation": "背景/情境",
            "task": "任务/目标",
            "action": "采取的行动",
            "result": "结果/收获",
            "skills": ["技能1", "技能2"],
            "relevance": "与求职的关联度（高/中/低）"
        }}
    ],
    "summary": "整体总结建议（100字以内）"
}}"""

    try:
        star_result_text = await chat_non_stream(
            messages=[{"role": "user", "content": star_prompt}],
            system_prompt="你是一位专业的职业规划师，擅长用STAR法则拆解经历。请只输出JSON格式。",
            max_tokens=1500,
        )
        # 尝试解析 JSON
        star_json = json.loads(star_result_text.strip().removeprefix("```json").removesuffix("```").strip())
    except (json.JSONDecodeError, Exception) as e:
        star_json = {
            "experiences": [],
            "summary": f"AI 分析暂时不可用，请稍后重试。错误: {str(e)[:100]}",
            "raw": star_result_text if 'star_result_text' in dir() else "",
        }

    return {"star_result": star_json, "user_id": req.user_id}


@router.post("/narrative")
async def narrative_reconstruct(req: NarrativeRequest, db: AsyncSession = Depends(get_db)):
    """叙事重构——从对话中挖掘个人故事并进行 STAR 拆解"""
    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if req.stage == "story_mining":
        # 阶段1：从对话中挖掘故事线索
        history_result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == req.user_id)
            .order_by(desc(Conversation.created_at))
            .limit(20)
        )
        history = list(reversed(history_result.scalars().all()))

        dialogue_text = ""
        for h in history:
            role_label = "用户" if h.role == "user" else "AI"
            dialogue_text += f"{role_label}: {h.content[:200]}\n"

        mining_prompt = f"""你是一位叙事心理学家。请根据以下对话历史，挖掘用户的关键人生/职业故事线索。

对话历史：
{dialogue_text}

请输出以下格式的 JSON（只输出 JSON）：
{{
    "stories": [
        {{
            "title": "故事标题",
            "theme": "主题（如：坚持、转变、突破、探索等）",
            "key_moment": "关键转折点描述",
            "emotion": "情感色彩",
            "insight": "从中获得的洞见",
            "quotes": ["用户原话片段"]
        }}
    ],
    "narrative_arc": "整体叙事弧线描述",
    "suggested_clues": ["建议进一步追问的方向1", "方向2"]
}}"""

        try:
            result_text = await chat_non_stream(
                messages=[{"role": "user", "content": mining_prompt}],
                system_prompt="你是一位叙事心理学家，擅长从对话中挖掘个人故事。请只输出JSON格式。",
                max_tokens=1200,
            )
            mining_json = json.loads(result_text.strip().removeprefix("```json").removesuffix("```").strip())
        except (json.JSONDecodeError, Exception) as e:
            mining_json = {
                "stories": [],
                "narrative_arc": f"分析暂时不可用: {str(e)[:100]}",
                "suggested_clues": [],
            }

        return {"stage": "story_mining", "result": mining_json}

    elif req.stage == "star_decomposition":
        # 阶段2：基于选定线索进行 STAR 拆解
        clues = req.clues or []
        content = req.content or ""

        star_prompt = f"""你是一位职业规划专家。请用 STAR 法则分析以下用户经历。

用户经历描述：
{content}

关键线索：{', '.join(clues) if clues else '无'}

请输出以下格式的 JSON（只输出 JSON）：
{{
    "experiences": [
        {{
            "title": "经历名称",
            "situation": "背景/情境",
            "task": "任务/目标",
            "action": "采取的行动",
            "result": "结果/收获",
            "skills": ["技能1", "技能2", "技能3"],
            "relevance": "与求职的关联度（高/中/低）"
        }}
    ],
    "summary": "整体建议（100字以内）",
    "highlights": ["亮点1", "亮点2"]
}}"""

        try:
            result_text = await chat_non_stream(
                messages=[{"role": "user", "content": star_prompt}],
                system_prompt="你是一位专业的职业规划师，擅长STAR法则。请只输出JSON格式。",
                max_tokens=1500,
            )
            star_json = json.loads(result_text.strip().removeprefix("```json").removesuffix("```").strip())
        except (json.JSONDecodeError, Exception) as e:
            star_json = {
                "experiences": [],
                "summary": f"分析暂时不可用: {str(e)[:100]}",
                "highlights": [],
            }

        return {"stage": "star_decomposition", "result": star_json}

    else:
        raise HTTPException(status_code=400, detail="无效的阶段类型，请使用 story_mining 或 star_decomposition")


# ---------- V4.1: 简历 & 面试辅助 ----------

class ResumeRequest(BaseModel):
    user_id: int
    target_position: str = ""
    position_keywords: list[str] = []
    experience_text: str = ""  # 前端直接传入的简历文本


class InterviewRequest(BaseModel):
    user_id: int
    target_position: str
    experiences: list[dict] = []


@router.post("/resume/rewrite")
async def rewrite_resume(req: ResumeRequest, db: AsyncSession = Depends(get_db)):
    """将经历改写为简历条目。优先使用前端传入的文本，否则从对话历史提取。"""
    from services.resume_service import ResumeWriter

    # 优先用前端传入的文本
    if req.experience_text.strip():
        raw_material = req.experience_text
    else:
        # 从对话历史提取
        result = await db.execute(select(User).where(User.id == req.user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        history_result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == req.user_id)
            .order_by(desc(Conversation.created_at))
            .limit(20)
        )
        history = list(reversed(history_result.scalars().all()))
        user_messages = [h.content for h in history if h.role == "user"]
        raw_material = "\n".join(user_messages[-8:])

    if not raw_material.strip():
        return {"error": "请先输入简历内容或在对话中描述你的经历"}

    # 改写
    rewritten = await ResumeWriter.rewrite_for_position(
        experience_text=raw_material,
        target_position=req.target_position or "通用岗位",
        position_keywords=req.position_keywords,
    )

    # 生成完整简历
    experiences = [{
        "title": req.target_position or "核心经历",
        "bullets": rewritten.get("bullets", []),
    }]
    resume = await ResumeWriter.generate_resume_summary(
        experiences=experiences,
        target_position=req.target_position or "通用岗位",
        name="",
    )

    return {
        "rewritten": rewritten,
        "resume": resume,
        "checklist": ResumeWriter.build_checklist(),
    }


@router.post("/interview/kit")
async def interview_kit(req: InterviewRequest, db: AsyncSession = Depends(get_db)):
    """一站式面试准备包：自我介绍 + 经历审计 + 常见问题 + 反问"""
    from services.resume_service import InterviewCoach

    result = await db.execute(select(User).where(User.id == req.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 从对话提取经历
    experiences = req.experiences
    if not experiences:
        history_result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == req.user_id)
            .order_by(desc(Conversation.created_at))
            .limit(20)
        )
        history = list(reversed(history_result.scalars().all()))
        experiences = []
        for h in history:
            if h.role == "user":
                experiences.append({
                    "title": h.content[:40],
                    "bullets": [h.content[:200]],
                })
        experiences = experiences[-5:]

    if not experiences:
        return {"error": "请先在对话中描述你的经历"}

    kit = await InterviewCoach.build_interview_kit(
        experiences=experiences,
        target_position=req.target_position,
        name=user.nickname or "",
    )

    return kit


# ============ 文件上传 + AI 处理 ============
import tempfile

def _extract_text_from_file(file_path: str, filename: str) -> str:
    """从上传的文件中提取文本内容"""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in ('.txt', '.md'):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()[:5000]
    
    elif ext == '.pdf':
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text[:5000]
        except ImportError:
            return "[PDF解析需要安装pypdf库]"
    
    elif ext in ('.docx', '.doc'):
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text[:5000]
        except ImportError:
            return "[Word解析需要安装python-docx库]"
    
    elif ext in ('.png', '.jpg', '.jpeg'):
        return "[图片文件：请使用文本输入框粘贴内容]"
    
    return "[不支持的文件格式]"


@router.post("/resume/upload")
async def upload_resume(
    user_id: int = Form(...),
    target_position: str = Form(""),
    resume_text: str = Form(""),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """上传简历文件 + 文本，AI 优化简历"""
    from services.resume_service import ResumeWriter
    
    content = resume_text or ""
    
    if file and file.filename:
        try:
            suffix = os.path.splitext(file.filename)[1] or ".tmp"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(await file.read())
                tmp_path = tmp.name
            extracted = _extract_text_from_file(tmp_path, file.filename)
            if content:
                content += "\n\n" + extracted
            else:
                content = extracted
            os.unlink(tmp_path)
        except Exception as e:
            content += f"\n[文件解析失败: {str(e)}，请使用文本输入框粘贴内容]"
    
    if not content.strip():
        return {"error": "请提供简历文本或上传文件"}
    
    rewritten = await ResumeWriter.rewrite_for_position(
        experience_text=content,
        target_position=target_position or "通用岗位",
        position_keywords=[],
    )
    
    experiences = [{"title": target_position or "核心经历", "bullets": rewritten.get("bullets", [])}]
    resume = await ResumeWriter.generate_resume_summary(
        experiences=experiences,
        target_position=target_position or "通用岗位",
        name="",
    )
    
    return {
        "rewritten": rewritten,
        "resume": resume,
        "checklist": ResumeWriter.build_checklist(),
    }


@router.post("/interview/upload")
async def upload_jd(
    user_id: int = Form(...),
    target_position: str = Form(""),
    jd_text: str = Form(""),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """上传JD文件 + 文本，生成面试准备包"""
    from services.resume_service import InterviewCoach
    
    content = jd_text or ""
    
    if file and file.filename:
        try:
            suffix = os.path.splitext(file.filename)[1] or ".tmp"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(await file.read())
                tmp_path = tmp.name
            extracted = _extract_text_from_file(tmp_path, file.filename)
            if content:
                content += "\n\n" + extracted
            else:
                content = extracted
            os.unlink(tmp_path)
        except Exception as e:
            content += f"\n[文件解析失败: {str(e)}，请使用文本输入框粘贴内容]"
    
    if not content.strip() and not target_position.strip():
        return {"error": "请提供JD文本、目标岗位或上传JD文件"}
    
    position = target_position or content[:50]
    
    # 用JD内容构建面试包
    experiences = [{"title": "目标岗位分析", "bullets": [content[:500]]}] if content else []
    
    kit = await InterviewCoach.build_interview_kit(
        experiences=experiences,
        target_position=position,
        name="",
        jd_text=content,
    )
    
    return kit


@router.post("/interview/full")
async def interview_full_prep(
    user_id: int = Form(...),
    target_position: str = Form(""),
    resume_text: str = Form(""),
    jd_text: str = Form(""),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """完整的面试准备：简历+JD（文本或文件），AI分析后生成面试问题
    
    接收单个文件（通过 file 字段），resume_text 和 jd_text 通过 formData 传入。
    文件内容会自动追加到对应的文本字段后面。
    """
    resume_content = resume_text or ""
    jd_content = jd_text or ""
    
    # 如果有文件，解析并追加到对应字段
    if file and file.filename:
        try:
            suffix = os.path.splitext(file.filename)[1] or ".tmp"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(await file.read())
                tmp_path = tmp.name
            extracted = _extract_text_from_file(tmp_path, file.filename)
            os.unlink(tmp_path)
            # 根据文件名判断是简历还是JD
            fname_lower = file.filename.lower()
            if 'jd' in fname_lower or 'job' in fname_lower or '岗位' in fname_lower or '职位' in fname_lower:
                jd_content = (jd_content + "\n" + extracted).strip()
            else:
                resume_content = (resume_content + "\n" + extracted).strip()
        except Exception as e:
            resume_content += f"\n[文件解析失败: {str(e)}]"
    
    if not resume_content.strip() and not jd_content.strip() and not target_position.strip():
        return {"error": "请提供简历内容、JD内容或目标岗位"}
    
    position = target_position or "目标岗位"
    
    prompt = f"""你是资深面试官。请根据以下简历和JD，生成一份完整的面试准备方案。

## 目标岗位
{position}

## 求职者简历
{resume_content[:2000] if resume_content else "（未提供）"}

## 岗位JD
{jd_content[:2000] if jd_content else "（未提供）"}

## 任务
分析简历与JD的匹配度，生成：
1. 面试官最可能追问的10个问题（按🔴必考/🟡高频/🟢可能分级）
2. 简历中的薄弱点（哪些地方可能被追问穿）
3. 30秒自我介绍（基于简历亮点，结合JD要求）
4. 建议反问面试官的3个问题

输出JSON：
{{
    "match_analysis": "简历与JD匹配度分析（50字）",
    "self_intro": "30秒自我介绍",
    "questions": [
        {{"level": "red|yellow|green", "question": "问题", "tip": "回答提示", "category": "简历相关|JD相关|行为面"}}
    ],
    "weak_spots": ["简历薄弱点1", "薄弱点2"],
    "reverse_questions": ["反问1", "反问2", "反问3"],
    "prep_checklist": ["准备事项1", "准备事项2", ...]
}}"""

    try:
        result = await chat_non_stream(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="你是资深面试官。只输出JSON。每个问题都要有针对性和可操作性。",
            max_tokens=2000,
        )
        cleaned = result.strip().removeprefix("```json").removesuffix("```").strip()
        interview_data = json.loads(cleaned)
    except Exception:
        interview_data = {
            "match_analysis": "分析生成中...",
            "self_intro": f"面试官好，我应聘{position}岗位。",
            "questions": [
                {"level": "red", "question": "请简单介绍你自己", "tip": "结合简历亮点，30秒", "category": "通用"},
                {"level": "red", "question": f"为什么选择{position}？", "tip": "展示对岗位的理解", "category": "JD相关"},
                {"level": "yellow", "question": "说说你最有代表性的项目", "tip": "STAR结构", "category": "简历相关"},
            ],
            "weak_spots": [],
            "reverse_questions": ["团队目前的工作方式是怎样的？"],
            "prep_checklist": ["准备30秒自我介绍", "熟悉简历每个细节", "了解公司业务"],
        }
    
    return interview_data
