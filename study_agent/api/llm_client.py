from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from study_agent.config import settings


@dataclass
class LLMResult:
    content: str
    used_remote_model: bool
    error: str | None = None


class OpenAICompatibleClient:
    """Minimal OpenAI-compatible Chat Completions client.

    The project can be demonstrated without credentials because each Agent has
    deterministic fallback logic. When OPENAI_API_KEY is configured, this client
    upgrades the output with a remote model call.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.openai_api_key
        self.base_url = (base_url or settings.openai_base_url).rstrip("/")
        self.model = model or settings.model
        self.timeout = timeout or settings.request_timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> LLMResult:
        if not self.enabled:
            return LLMResult(
                content="",
                used_remote_model=False,
                error="OPENAI_API_KEY 未配置，已使用本地规则引擎输出。",
            )

        payload: dict[str, Any] = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        request = urllib.request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)
                content = data["choices"][0]["message"]["content"]
                return LLMResult(content=content, used_remote_model=True)
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as exc:
            return LLMResult(content="", used_remote_model=False, error=str(exc))

