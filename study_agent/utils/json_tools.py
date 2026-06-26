from __future__ import annotations

import json
import re
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first JSON object from model output."""
    text = text.strip()
    if not text:
        return {}

    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            value = json.loads(text[start : end + 1])
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            return {}

    return {}


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)

