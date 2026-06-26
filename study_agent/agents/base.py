from __future__ import annotations

from typing import Any

from study_agent.api.llm_client import OpenAICompatibleClient
from study_agent.memory.storage import JsonMemoryStore
from study_agent.utils.json_tools import extract_json_object


class BaseAgent:
    def __init__(
        self,
        memory: JsonMemoryStore | None = None,
        llm: OpenAICompatibleClient | None = None,
    ) -> None:
        self.memory = memory or JsonMemoryStore()
        self.llm = llm or OpenAICompatibleClient()

    def ask_model_json(self, system_prompt: str, user_prompt: str) -> tuple[dict[str, Any], str | None]:
        result = self.llm.complete_json(system_prompt, user_prompt)
        if not result.used_remote_model:
            return {}, result.error
        parsed = extract_json_object(result.content)
        if not parsed:
            return {}, "模型未返回可解析 JSON，已使用本地规则引擎输出。"
        return parsed, None

