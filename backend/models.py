"""SQLAlchemy 数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(128), unique=True, nullable=False, index=True)
    nickname = Column(String(64), default="")
    avatar_url = Column(String(512), default="")

    # 三维画像
    major_category = Column(String(32), default="")       # science/engineering/arts/...
    major_name = Column(String(64), default="")             # 具体专业名
    education_type = Column(String(32), default="")         # domestic_bachelor/overseas_master/...
    grade = Column(String(32), default="")                  # freshman/sophomore/junior/...
    current_stage = Column(String(8), default="S1")         # S1-S7
    target_industries = Column(JSON, default=list)          # ["internet", "finance"]

    # 时间线
    graduation_year = Column(Integer, nullable=True)        # 入学年份
    onboarding_completed = Column(Integer, default=0)       # 0=未完成引导, 1=已完成
    target_role = Column(String(128), default="")           # 目标岗位
    
    # 求职状态与清晰度
    career_clarity = Column(String(32), default="")         # very_clear/somewhat_clear/exploring/unclear
    current_status = Column(String(32), default="")         # studying/internship/job_hunting/...
    
    # 静默模式
    silent_mode = Column(Integer, default=0)                # 0=关闭, 1=开启
    silent_until = Column(DateTime, nullable=True)
    anxiety_level = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    stage_logs = relationship("StageLog", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(16), nullable=False)               # user / assistant / system
    content = Column(Text, nullable=False)
    context_stage = Column(String(8), default="")           # 对话时的用户阶段
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")


class StageLog(Base):
    """阶段变更日志"""
    __tablename__ = "stage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    from_stage = Column(String(8), default="")
    to_stage = Column(String(8), nullable=False)
    reason = Column(String(256), default="")                # 变更原因
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="stage_logs")


class ContentItem(Base):
    """推荐内容库"""
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    type = Column(String(32), nullable=False)               # industry_intro/major_map/resume_review/...
    stage_tag = Column(String(8), default="")               # 适用阶段 S1-S7
    industry_tag = Column(String(32), default="")           # 适用行业
    major_tag = Column(String(32), default="")              # 适用专业大类
    content = Column(Text, default="")                      # 内容正文（Markdown）
    url = Column(String(512), default="")                   # 外部链接
    sort_order = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class OnboardingAnswer(Base):
    """引导问卷回答记录"""
    __tablename__ = "onboarding_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_key = Column(String(64), nullable=False)
    answer_value = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------- Holland & Radar ----------

class RadarChart(Base):
    """能力雷达图"""
    __tablename__ = "radar_charts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    version = Column(Integer, default=1)
    generated_from = Column(String(32), default="")  # holland / dialog
    dimensions = Column(JSON, default=list)    # [{name, confidence, ...}]
    interpretation = Column(Text, default="")
    matched_roles = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class Memory(Base):
    """用户记忆/叙事素材"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    memory_type = Column(String(32), default="")  # holland / radar / milestone / experience
    content = Column(Text, default="")
    importance = Column(Integer, default=3)  # 1-5
    created_at = Column(DateTime, default=datetime.utcnow)


class StoryMaterial(Base):
    """叙事素材"""
    __tablename__ = "story_materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(128), default="")
    raw_content = Column(Text, default="")
    star_content = Column(JSON, default=dict)
    trait_revealed = Column(String(256), default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationPhase(Base):
    """对话阶段追踪"""
    __tablename__ = "conversation_phases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    current_phase = Column(String(32), default="depth1")
    interest_clues = Column(JSON, default=list)
    explore_directions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------- Roadmap & Milestones ----------

class Roadmap(Base):
    """成长路线图"""
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    template_key = Column(String(64), default="general")
    target_role = Column(String(128), default="")
    total_progress = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class RoadmapStage(Base):
    """路线图阶段"""
    __tablename__ = "roadmap_stages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    name = Column(String(64), default="")
    icon = Column(String(16), default="")
    sort_order = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    status = Column(String(16), default="pending")


class Milestone(Base):
    """里程碑"""
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stage_id = Column(Integer, ForeignKey("roadmap_stages.id"), nullable=False)
    name = Column(String(128), default="")
    verification = Column(String(256), default="")
    estimated_hours = Column(Float, default=0.0)
    status = Column(String(16), default="pending")  # pending / in_progress / completed
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserMilestone(Base):
    """用户自定义里程碑"""
    __tablename__ = "user_milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(128), default="")
    verification = Column(String(256), default="")
    sort_order = Column(Integer, default=0)
    status = Column(String(16), default="pending")  # pending / in_progress / completed
    completed_at = Column(DateTime, nullable=True)
    reflection = Column(Text, default="")
    reflection_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MicroTask(Base):
    """微任务"""
    __tablename__ = "micro_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    content = Column(String(256), default="")
    estimated_minutes = Column(Integer, default=15)
    status = Column(String(16), default="pending")  # pending / completed
    task_date = Column(String(16), default="")  # YYYY-MM-DD
    sort_order = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WeeklySummary(Base):
    """每周总结"""
    __tablename__ = "weekly_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    week_start = Column(String(16), nullable=True)  # YYYY-MM-DD
    week_end = Column(String(16), nullable=True)
    completed_tasks = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    milestones_completed = Column(JSON, default=list)
    highlights = Column(JSON, default=list)
    ai_summary = Column(Text, default="")
    next_week_advice = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------- Anxiety ----------

class AnxietyLog(Base):
    """焦虑记录"""
    __tablename__ = "anxiety_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    trigger_type = Column(String(32), default="active")  # active / passive
    emotion_type = Column(String(32), default="")  # 情绪类型
    user_input = Column(Text, default="")
    ai_response = Column(Text, default="")
    micro_action = Column(String(256), default="")
    completed_action = Column(Integer, default=0)  # 0/1
    created_at = Column(DateTime, default=datetime.utcnow)
