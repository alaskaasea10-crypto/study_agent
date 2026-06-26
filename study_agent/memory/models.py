from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class MistakeRecord:
    description: str
    error_type: str
    knowledge_point: str
    advice: str
    course: str = "未指定课程"
    created_at: str = field(default_factory=now_iso)
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StudyRecord:
    content: str
    summary: str
    problems: list[str]
    tomorrow_suggestions: list[str]
    created_at: str = field(default_factory=now_iso)
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PlanRecord:
    course: str
    exam_date: str
    plan: dict[str, Any]
    created_at: str = field(default_factory=now_iso)
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

