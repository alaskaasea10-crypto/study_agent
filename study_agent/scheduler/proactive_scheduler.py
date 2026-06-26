from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from study_agent.memory.storage import JsonMemoryStore


class ProactiveScheduler:
    """Simple time-triggered proactive layer.

    In a production HarmonyOS app this layer can be replaced by system alarms,
    calendar events, or push notifications. For the MVP it creates proactive
    cards when the command is run or when demo simulation is requested.
    """

    def __init__(self, memory: JsonMemoryStore | None = None) -> None:
        self.memory = memory or JsonMemoryStore()

    def generate_cards(self, now: datetime | None = None, simulate: bool = False) -> list[dict[str, Any]]:
        current = now or datetime.now()
        data = self.memory.load()
        cards: list[dict[str, Any]] = []

        hour = current.hour
        if simulate or 7 <= hour <= 9:
            cards.append(self._morning_card(data))
        if simulate or 12 <= hour <= 14:
            cards.append(self._midday_card(data))
        if simulate or 21 <= hour <= 23:
            cards.append(self._evening_card(data))

        weak_card = self._weak_point_card(data)
        if weak_card:
            cards.append(weak_card)

        for card in cards:
            self.memory.save_scheduler_event(card)
        return cards

    def _base_card(self, trigger: str, title: str, message: str, action: str) -> dict[str, Any]:
        return {
            "id": str(uuid4()),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "trigger": trigger,
            "title": title,
            "message": message,
            "suggested_action": action,
        }

    def _morning_card(self, data: dict[str, Any]) -> dict[str, Any]:
        latest_plan = data.get("plans", [])[-1:] or []
        if latest_plan:
            course = latest_plan[0].get("course", "最近课程")
            message = f"早上好。今天先完成 {course} 计划中的第一个检查点，再进入新任务。"
        else:
            message = "早上好。你还没有创建考试计划，建议先为最近一门考试生成复习安排。"
        return self._base_card("morning_check", "晨间学习启动", message, "打开今日计划")

    def _midday_card(self, data: dict[str, Any]) -> dict[str, Any]:
        mistakes = data.get("mistakes", [])
        if mistakes:
            point = mistakes[-1].get("knowledge_point", "最近错题")
            message = f"午间适合做一次轻复盘：用 10 分钟回看“{point}”。"
        else:
            message = "午间适合做一次轻复盘：任选上午学过的 1 个概念，用自己的话讲一遍。"
        return self._base_card("midday_review", "午间轻复盘", message, "记录复盘结果")

    def _evening_card(self, data: dict[str, Any]) -> dict[str, Any]:
        records = data.get("study_records", [])
        if records:
            message = "今晚建议补一条学习总结：完成内容、卡点、明日优先级各写一句。"
        else:
            message = "今天还没有学习总结。写下 3 句话，Agent 明天会据此调整计划。"
        return self._base_card("evening_summary", "晚间总结提醒", message, "生成今日总结")

    def _weak_point_card(self, data: dict[str, Any]) -> dict[str, Any] | None:
        mistakes = data.get("mistakes", [])
        counter: dict[str, int] = {}
        for mistake in mistakes:
            point = mistake.get("knowledge_point", "未分类")
            counter[point] = counter.get(point, 0) + 1
        if not counter:
            return None
        point, count = max(counter.items(), key=lambda item: item[1])
        if count < 2:
            return None
        return self._base_card(
            "weak_point_detected",
            "薄弱点专项提醒",
            f"“{point}”已经出现 {count} 次，建议安排 20 分钟专项训练。",
            "生成专项练习清单",
        )

