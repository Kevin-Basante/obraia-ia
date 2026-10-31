"""Creates the analyzer chosen in the settings."""

from functools import lru_cache

from app.analyzers.base import BlueprintAnalyzer
from app.analyzers.fake import FakeAnalyzer
from app.analyzers.gemini import GeminiAnalyzer
from app.config import get_settings


@lru_cache
def get_analyzer() -> BlueprintAnalyzer:
    settings = get_settings()
    if settings.analyzer == "fake":
        return FakeAnalyzer()
    return GeminiAnalyzer(settings.gemini_api_key, settings.gemini_model)
