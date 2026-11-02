"""Creates the analyzer chosen in the settings (Factory) and wraps it with its decorators."""

from functools import lru_cache

from app.analyzers.base import BlueprintAnalyzer
from app.analyzers.fake import FakeAnalyzer
from app.analyzers.fallback import FallbackAnalyzer
from app.analyzers.gemini import GeminiAnalyzer
from app.analyzers.retrying import RetryingAnalyzer
from app.config import Settings, get_settings


def build_gemini(settings: Settings) -> BlueprintAnalyzer:
    """The main model with its retries; when there is a different backup model, it gets its own retries."""

    def with_retries(model: str) -> BlueprintAnalyzer:
        return RetryingAnalyzer(GeminiAnalyzer(settings.gemini_api_key, model), retries=settings.gemini_retries)

    main = with_retries(settings.gemini_model)
    backup = settings.gemini_fallback_model
    if not backup or backup == settings.gemini_model:
        return main
    return FallbackAnalyzer(main, with_retries(backup))


@lru_cache
def get_analyzer() -> BlueprintAnalyzer:
    settings = get_settings()
    if settings.analyzer == "fake":
        return FakeAnalyzer()
    return build_gemini(settings)
