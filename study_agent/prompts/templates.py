from __future__ import annotations

import json
from typing import Any


BASE_SYSTEM_PROMPT = """
你是“学伴 Study Agent”，一个面向大学生的主动服务型学习智能体。
你不是闲聊机器人，而是学习行为管理系统：需要结合历史记录、错题、考试节点和用户状态，给出可执行、可跟踪、可复盘的建议。
请始终输出严格 JSON，不要输出 Markdown。
""".strip()


PLAN_PROMPT = """
请为大学生生成学习计划。
输入信息：
{payload}

要求：
1. 输出每日学习安排，包含日期、学习主题、任务、时长、检查点。
2. 输出分阶段复习策略。
3. 必须结合历史错题和学习记录，体现主动调整。
4. JSON 字段必须包含：daily_plan, phases, adaptive_reason, risk_alerts。
""".strip()


MISTAKE_PROMPT = """
请分析大学生的一道错题。
输入信息：
{payload}

要求：
1. 判断错误类型。
2. 提取知识点。
3. 给出复习建议和下次练习策略。
4. 结合历史高频错误，判断是否需要专项提醒。
5. JSON 字段必须包含：error_type, knowledge_point, cause, review_advice, next_practice, proactive_alert。
""".strip()


SUMMARY_PROMPT = """
请生成大学生今日学习总结。
输入信息：
{payload}

要求：
1. 总结今日学习内容。
2. 分析可能的问题。
3. 给出明日建议。
4. 结合历史错题和计划完成情况，体现个性化调整。
5. JSON 字段必须包含：summary, problem_analysis, tomorrow_suggestions, memory_update_hint, proactive_follow_up。
""".strip()


def render(template: str, payload: dict[str, Any]) -> str:
    return template.format(payload=json.dumps(payload, ensure_ascii=False, indent=2))

