from __future__ import annotations

from datetime import timedelta
from typing import Any

from study_agent.agents.base import BaseAgent
from study_agent.memory.models import PlanRecord
from study_agent.prompts.templates import BASE_SYSTEM_PROMPT, PLAN_PROMPT, render
from study_agent.utils.time_tools import days_until, parse_date, today


class LearningPlanAgent(BaseAgent):
    def generate(self, course: str, exam_date: str, daily_hours: float = 2.0) -> dict[str, Any]:
        exam_day = parse_date(exam_date)
        remaining_days = max(days_until(exam_day), 1)
        context = self.memory.recent_context()

        payload = {
            "course": course,
            "exam_date": exam_date,
            "daily_hours": daily_hours,
            "remaining_days": remaining_days,
            "memory_context": context,
        }
        model_plan, model_error = self.ask_model_json(
            BASE_SYSTEM_PROMPT,
            render(PLAN_PROMPT, payload),
        )
        plan = self._fallback_plan(course, exam_date, daily_hours, context)

        if model_plan:
            plan.update({key: value for key, value in model_plan.items() if value})
            plan["source"] = "llm"
        else:
            plan["source"] = "local_engine"
            plan["model_note"] = model_error

        self.memory.save_plan(PlanRecord(course=course, exam_date=exam_date, plan=plan))
        return plan

    def _fallback_plan(
        self,
        course: str,
        exam_date: str,
        daily_hours: float,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        exam_day = parse_date(exam_date)
        start = today()
        total_days = max((exam_day - start).days, 1)
        weak_points = context.get("weak_points", [])
        weak_point_names = [item["knowledge_point"] for item in weak_points[:3]]

        daily_plan: list[dict[str, Any]] = []
        for index in range(total_days):
            current = start + timedelta(days=index)
            days_left = (exam_day - current).days
            stage = self._stage_name(index, total_days)
            focus = self._focus_for_stage(stage, course, weak_point_names)
            daily_plan.append(
                {
                    "date": current.isoformat(),
                    "stage": stage,
                    "theme": focus,
                    "tasks": [
                        f"梳理 {course} 核心概念 30 分钟",
                        "完成 8-12 道典型题并记录错因",
                        "用 10 分钟复盘今天最卡住的一个知识点",
                    ],
                    "duration_hours": daily_hours,
                    "checkpoint": "能否不看答案讲清 1 个概念，并独立完成同类题。",
                    "days_to_exam": days_left,
                }
            )

        phases = [
            {
                "name": "基础重建",
                "range": "前 40% 时间",
                "strategy": "建立章节地图，优先补齐概念、公式、定义和基础例题。",
            },
            {
                "name": "专题突破",
                "range": "中间 40% 时间",
                "strategy": "围绕错题高频知识点做专项训练，每个专题形成一页复盘卡。",
            },
            {
                "name": "考前冲刺",
                "range": "最后 20% 时间",
                "strategy": "做整卷模拟、限时训练和错题回看，减少低级失误。",
            },
        ]

        risk_alerts = []
        if weak_point_names:
            risk_alerts.append(f"历史错题集中在：{'、'.join(weak_point_names)}，计划中已提高这些知识点的复习权重。")
        if total_days <= 7:
            risk_alerts.append("距离考试不足 7 天，建议减少新内容扩张，转向错题回炉和高频题型。")

        return {
            "course": course,
            "exam_date": exam_date,
            "daily_plan": daily_plan,
            "phases": phases,
            "adaptive_reason": "根据历史错题、近期学习记录和考试倒计时动态分配复习重点。",
            "risk_alerts": risk_alerts or ["当前风险较低，建议持续记录错题以便后续自适应调整。"],
        }

    def _stage_name(self, index: int, total_days: int) -> str:
        ratio = (index + 1) / max(total_days, 1)
        if ratio <= 0.4:
            return "基础重建"
        if ratio <= 0.8:
            return "专题突破"
        return "考前冲刺"

    def _focus_for_stage(self, stage: str, course: str, weak_points: list[str]) -> str:
        if stage == "专题突破" and weak_points:
            return f"{course} 专项突破：{weak_points[0]}"
        if stage == "考前冲刺" and weak_points:
            return f"{course} 模拟训练 + 错题回看：{weak_points[0]}"
        return f"{course} 章节基础与知识框架"

