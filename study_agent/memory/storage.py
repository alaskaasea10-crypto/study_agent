from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from study_agent.config import settings
from study_agent.memory.models import MistakeRecord, PlanRecord, StudyRecord


DEFAULT_MEMORY: dict[str, Any] = {
    "mistakes": [],
    "study_records": [],
    "plans": [],
    "scheduler_events": [],
}


class JsonMemoryStore:
    """Persistent local memory for the Study Agent."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or settings.memory_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(DEFAULT_MEMORY)

    def load(self) -> dict[str, Any]:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            data = DEFAULT_MEMORY.copy()

        for key, value in DEFAULT_MEMORY.items():
            data.setdefault(key, [] if isinstance(value, list) else value)
        return data

    def _write(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def save_mistake(self, record: MistakeRecord) -> None:
        data = self.load()
        data["mistakes"].append(record.to_dict())
        self._write(data)

    def save_study_record(self, record: StudyRecord) -> None:
        data = self.load()
        data["study_records"].append(record.to_dict())
        self._write(data)

    def save_plan(self, record: PlanRecord) -> None:
        data = self.load()
        data["plans"].append(record.to_dict())
        self._write(data)

    def save_scheduler_event(self, event: dict[str, Any]) -> None:
        data = self.load()
        data["scheduler_events"].append(event)
        self._write(data)

    def recent_context(self, limit: int = 5) -> dict[str, Any]:
        data = self.load()
        mistakes = data["mistakes"][-limit:]
        study_records = data["study_records"][-limit:]
        plans = data["plans"][-limit:]
        return {
            "recent_mistakes": mistakes,
            "recent_study_records": study_records,
            "recent_plans": plans,
            "weak_points": self.weak_points(top_k=5),
            "error_type_stats": self.error_type_stats(),
        }

    def weak_points(self, top_k: int = 5) -> list[dict[str, Any]]:
        mistakes = self.load()["mistakes"]
        counter = Counter(item.get("knowledge_point", "未分类") for item in mistakes)
        return [{"knowledge_point": key, "count": value} for key, value in counter.most_common(top_k)]

    def error_type_stats(self) -> list[dict[str, Any]]:
        mistakes = self.load()["mistakes"]
        counter = Counter(item.get("error_type", "未分类") for item in mistakes)
        return [{"error_type": key, "count": value} for key, value in counter.most_common()]

