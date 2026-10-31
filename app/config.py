"""Settings read from environment variables (Render dashboard or a local .env file)."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DEFAULT_MODEL = "gemini-3.5-flash"


def _load_dotenv(path: Path = Path(".env")) -> None:
    """Loads KEY=value lines into the environment, without overriding real variables."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    """Values the service needs to run.

    analyzer: "gemini" reads blueprints with Gemini; "fake" returns fixed
    measurements, for local development without an API key.
    service_token: shared secret that the backend sends in X-Service-Token.
    """

    analyzer: str
    gemini_api_key: str
    gemini_model: str
    service_token: str
    max_file_mb: int

    @property
    def max_file_bytes(self) -> int:
        return self.max_file_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    _load_dotenv()
    return Settings(
        analyzer=os.environ.get("ANALYZER", "gemini").strip().lower(),
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        gemini_model=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL),
        service_token=os.environ.get("SERVICE_TOKEN", ""),
        max_file_mb=int(os.environ.get("MAX_FILE_MB", "10")),
    )
