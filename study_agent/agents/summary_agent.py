from __future__ import annotations

from typing import Any

from study_agent.agents.base import BaseAgent
from study_agent.memory.models import StudyRecord
from study_agent.prompts.templates import BASE_SYSTEM_PROMPT, SUMMARY_PROMPT, render


class LearningSummaryAgent(BaseAgent):
    def summarize(self, content: str) -> dict[str, Any]:
        context = self.memory.recent_context()
        payload = {
            "today_content": content,
            "memory_context": context,
        }

        model_summary, model_error = self.ask_model_json(
            BASE_SYSTEM_PROMPT,
            render(SUMMARY_PROMPT, payload),
        )
        summary = self._fallback_summary(content, context)

        if model_summary:
            summary.update({key: value for key, value in model_summary.items() if value})
            summary["source"] = "llm"
        else:
            summary["source"] = "local_engine"
            summary["model_note"] = model_error

        self.memory.save_study_record(
            StudyRecord(
                content=content,
                summary=str(summary["summary"]),
                problems=self._as_list(summary["problem_analysis"]),
                tomorrow_suggestions=self._as_list(summary["tomorrow_suggestions"]),
            )
        )
        return summary

    def _fallback_summary(self, content: str, context: dict[str, Any]) -> dict[str, Any]:
        weak_points = [item["knowledge_point"] for item in context.get("weak_points", [])[:3]]
        problem_analysis = [
            "今日内容已记录，但建议补充“完成度、正确率、耗时”三个量化指标。",
            "如果只看课本不做题，系统会判断为输入型学习偏多，需要加入输出训练。",
        ]
        if weak_points:
            problem_analysis.append(f"历史薄弱点仍集中在：{'、'.join(weak_points)}，明日任务应优先覆盖。")

        tomorrow = [
            "先用 15 分钟回顾今日笔记，写出 3 个关键词。",
            "围绕今日最不熟的知识点做 5 道小题，错题立即入库。",
            "晚上用 5 分钟更新完成度，便于 Agent 明天主动调整计划。",
        ]
        if weak_points:
            tomorrow.insert(1, f"专项复习薄弱点：{weak_points[0]}，至少完成 2 道同类题。")

        return {
            "summary": f"今天的学习重点是：{content[:120]}{'...' if len(content) > 120 else ''}",
            "problem_analysis": problem_analysis,
            "tomorrow_suggestions": tomorrow,
            "memory_update_hint": "已把今日学习内容写入长期记忆，后续计划会参考这次记录。",
            "proactive_follow_up": "若明天 21:30 前没有学习总结，系统会生成一次模拟提醒。",
        }

    def _as_list(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]

