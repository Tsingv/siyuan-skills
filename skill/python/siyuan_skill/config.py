from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_HOST = "http://127.0.0.1:6806"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
CACHE_FILE = Path.home() / ".cache" / "siyuan-skill" / "token.json"


def _load_project_env() -> None:
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=False)


@dataclass(slots=True)
class SiYuanConfig:
    host: str = DEFAULT_HOST
    token: str = ""
    password: str = ""
    timeout: float = 20.0
    default_format: str = "json"
    env_file: Path = ENV_FILE
    cache_file: Path = CACHE_FILE
    project_root: Path = PROJECT_ROOT

    @classmethod
    def load(
        cls,
        *,
        host: str | None = None,
        token: str | None = None,
        password: str | None = None,
        timeout: float | None = None,
        default_format: str | None = None,
    ) -> "SiYuanConfig":
        _load_project_env()
        return cls(
            host=(host or os.getenv("SIYUAN_HOST") or DEFAULT_HOST).rstrip("/"),
            token=token if token is not None else os.getenv("SIYUAN_TOKEN", ""),
            password=password if password is not None else os.getenv("PASSWORD", ""),
            timeout=float(timeout if timeout is not None else os.getenv("SIYUAN_TIMEOUT", "20")),
            default_format=(default_format or os.getenv("SIYUAN_OUTPUT_FORMAT") or "json").lower(),
        )

    def ensure_cache_parent(self) -> None:
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
