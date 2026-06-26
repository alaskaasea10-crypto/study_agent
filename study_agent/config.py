from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def _env(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


@dataclass(frozen=True)
class Settings:
    app_name: str = "学伴 Study Agent"
    data_dir: Path = Path(_env("STUDY_AGENT_DATA_DIR", str(PROJECT_ROOT / "data")))
    openai_api_key: str = _env("OPENAI_API_KEY", "")
    openai_base_url: str = _env("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model: str = _env("STUDY_AGENT_MODEL", "gpt-4.1-mini")
    request_timeout: int = int(_env("STUDY_AGENT_TIMEOUT", "25"))

    @property
    def memory_path(self) -> Path:
        return self.data_dir / "memory.json"


settings = Settings()
