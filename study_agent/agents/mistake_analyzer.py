from __future__ import annotations

import re
from typing import Any

from study_agent.agents.base import BaseAgent
from study_agent.memory.models import MistakeRecord
from study_agent.prompts.templates import BASE_SYSTEM_PROMPT, MISTAKE_PROMPT, render


class MistakeAnalysisAgent(BaseAgent):
    ERROR_RULES = [
        ("概念理解错误", ["概念", "定义", "本质", "理解错", "不会判断"]),
        ("公式/定理使用错误", ["公式", "定理", "推导", "套错", "符号"]),
        ("计算失误", ["计算", "算错", "粗心", "小数", "符号错"]),
        ("审题偏差", ["看错", "题意", "条件", "忽略", "单位"]),
        ("方法选择不当", ["方法", "思路", "不会下手", "模型", "步骤"]),
    ]

    def analyze(self, description: str, course: str = "未指定课程") -> dict[str, Any]:
        context = self.memory.recent_context()
        payload = {
            "course": course,
            "mistake_description": description,
            "memory_context": context,
        }

        model_analysis, model_error = self.ask_model_json(
            BASE_SYSTEM_PROMPT,
            render(MISTAKE_PROMPT, payload),
        )
        analysis = self._fallback_analysis(description, course, context)

        if model_analysis:
            analysis.update({key: value for key, value in model_analysis.items() if value})
            analysis["source"] = "llm"
        else:
            analysis["source"] = "local_engine"
            analysis["model_note"] = model_error

        self.memory.save_mistake(
            MistakeRecord(
                description=description,
                course=course,
                error_type=str(analysis["error_type"]),
                knowledge_point=str(analysis["knowledge_point"]),
                advice=str(analysis["review_advice"]),
            )
        )
        return analysis

    def _fallback_analysis(
        self,
        description: str,
        course: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        error_type = "方法选择不当"
        for candidate, keywords in self.ERROR_RULES:
            if any(keyword in description for keyword in keywords):
                error_type = candidate
                break

        knowledge_point = self._extract_knowledge_point(description, course)
        weak_points = context.get("weak_points", [])
        repeated = any(item["knowledge_point"] == knowledge_point and item["count"] >= 2 for item in weak_points)

        return {
            "course": course,
            "error_type": error_type,
            "knowledge_point": knowledge_point,
            "cause": self._cause_for(error_type),
            "review_advice": [
                f"把“{knowledge_point}”整理成一张概念卡：定义、适用条件、常见陷阱各写 1 条。",
                "找 3 道同类型题做二次训练，并记录每道题的第一步判断依据。",
                "明天复习开始前先用 5 分钟口述这道题的正确思路。",
            ],
            "next_practice": {
                "difficulty": "基础题 2 道 + 中等题 2 道 + 限时题 1 道",
                "checkpoint": "看到同类题时，能先判断知识点和方法，再开始计算。",
            },
            "proactive_alert": (
                f"该知识点“{knowledge_point}”已多次出现，系统会在下次学习计划中自动提高它的复习优先级。"
                if repeated
                else "已写入错题记忆；若后续重复出现，系统会触发专项复习提醒。"
            ),
        }

    def _extract_knowledge_point(self, description: str, course: str) -> str:
        patterns = [
            r"知识点[:：]\s*([^。；;\n]+)",
            r"关于\s*([^，。；;\n]+)",
            r"在\s*([^，。；;\n]+)\s*(?:这里|部分|题)",
        ]
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(1).strip()
        return f"{course} 高频基础知识点"

    def _cause_for(self, error_type: str) -> str:
        mapping = {
            "概念理解错误": "概念边界不清，容易把相似定义混在一起。",
            "公式/定理使用错误": "公式适用条件没有先判断，导致套用路径错误。",
            "计算失误": "步骤检查不足，符号、单位或中间量没有复核。",
            "审题偏差": "题干条件没有结构化提取，遗漏了限制信息。",
            "方法选择不当": "没有形成题型到方法的稳定映射。",
        }
        return mapping.get(error_type, "需要通过复盘定位稳定错因。")

