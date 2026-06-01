"""一步(StepOne) · 留白机制 + 焦虑急救包 · V3.0"""
import random
from datetime import datetime
from data_definitions import ANXIETY_FLOW, EMOTION_KEYWORDS


def detect_emotion_type(text: str) -> str:
    """检测文本中的情绪类型"""
    for emotion_type, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return emotion_type
    return "anxiety"


def should_trigger_anxiety(text: str) -> bool:
    """判断是否应该触发焦虑急救"""
    count = 0
    for keywords in EMOTION_KEYWORDS.values():
        for kw in keywords:
            if kw in text:
                count += 1
    return count >= 1


# ============ V3.0 留白机制 ============

def should_suggest_break(
    recent_messages: list[str],
    current_hour: int,
    anxiety_level: int,
    silent_mode: bool,
) -> dict:
    """判断是否应该建议留白/休息"""
    if silent_mode:
        return {"should_break": False, "reason": ""}

    # 1. 深夜活跃检测
    if current_hour >= 23 or current_hour <= 5:
        return {
            "should_break": True,
            "reason": "late_night",
            "message": "这么晚了还在努力，辛苦了。但身体是革命的本钱，明天效率会更高。现在去睡吧，我在这里。",
            "suggest_silent": False,
        }

    # 2. 高频焦虑检测
    anxiety_count = 0
    for msg in recent_messages[-5:]:
        if should_trigger_anxiety(msg):
            anxiety_count += 1
    if anxiety_count >= 3:
        return {
            "should_break": True,
            "reason": "high_anxiety",
            "message": "我感觉到你最近压力很大。这周要不要先不聊求职了？去读本书、看部电影，或者只是睡个好觉。路还在那里，不会跑。",
            "suggest_silent": True,
        }

    # 3. 焦虑等级过高
    if anxiety_level >= 7:
        return {
            "should_break": True,
            "reason": "high_anxiety_level",
            "message": "你现在的焦虑指数有点高。有时候最好的前进，是先停下来。要不要试试「静默模式」？这周不聊求职，只做让自己开心的事。",
            "suggest_silent": True,
        }

    return {"should_break": False, "reason": ""}


def get_anxiety_flow(emotion_type: str, user_input: str) -> dict:
    """获取焦虑急救三步流程"""
    flow = {
        "step1": {
            "title": ANXIETY_FLOW["step1"]["title"],
            "duration": ANXIETY_FLOW["step1"]["duration"],
            "content": _build_step1_response(emotion_type, user_input),
        },
        "step2": {
            "title": ANXIETY_FLOW["step2"]["title"],
            "duration": ANXIETY_FLOW["step2"]["duration"],
            "content": _build_step2_response(emotion_type, user_input),
        },
        "step3": {
            "title": ANXIETY_FLOW["step3"]["title"],
            "duration": ANXIETY_FLOW["step3"]["duration"],
            "micro_action": random.choice(ANXIETY_FLOW["step3"]["micro_actions"]),
        },
    }
    return flow


def _build_step1_response(emotion_type: str, user_input: str) -> str:
    emotion_map = {
        "anxiety": "焦虑和压力",
        "rejection": "失落和挫败",
        "self_doubt": "自我怀疑",
        "confusion": "迷茫",
        "exhaustion": "疲惫和倦怠",
    }
    emotion_text = emotion_map.get(emotion_type, "一些情绪波动")
    responses = [
        f"我听到了，你现在感受到{emotion_text}。这完全正常，求职路上每个人都会经历这样的时刻。你愿意多说说发生了什么吗？",
        f"嗯，{emotion_text}是不好受的。但你能说出来，这本身就很勇敢。要不要和我聊聊具体是什么让你有这样的感受？",
    ]
    return random.choice(responses)


def _build_step2_response(emotion_type: str, user_input: str) -> str:
    reframes = {
        "rejection": "面试被拒 ≠ 你不行。面试是双向匹配的过程，有很多因素不在你的控制范围内——岗位匹配度、面试官偏好、甚至运气。很多优秀的人当初也被拒过很多次。让我们区分两件事：'这个结果不理想'（事实）和'我不够好'（你的解读）。",
        "self_doubt": "当你说'我不行'的时候，试着把它换成'我目前在这个方面还需要提升'。这是完全不同的两件事。你已经拿了面试机会，说明简历是过关的；你已经走到了现在，说明你一直在前进。不要用几场面试的结果来否定自己所有的努力。",
        "anxiety": "焦虑是身体的预警信号，说明你真的很在意这件事。适度的焦虑其实是动力——很多人的最佳表现都是在适度压力下产生的。但如果焦虑让你无法行动，我们就需要先放慢一下。",
        "confusion": "迷茫是成长的必经之路。不知道自己想要什么，不等于你很差劲——恰恰相反，这说明你在认真思考，而不是随波逐流。",
        "exhaustion": "累了是身体在告诉你需要休息，这不是软弱，是智慧。机器都要关机维护，何况是人。今天可以不用push自己。",
    }
    return reframes.get(emotion_type, "有些事情不在你的控制范围内，但你在你能控制的事情上已经做得很好了。")


def get_silent_mode_message() -> str:
    """静默模式欢迎消息"""
    return "🌿 你已进入静默模式\n\n这周，你的任务就是：\n▸ 好好吃饭\n▸ 好好睡觉\n▸ 做点与求职无关但让你开心的事\n\n路还在那里，不会跑。\n我在这里，随时等你回来。"
