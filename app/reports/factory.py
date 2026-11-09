"""Creates the summary writer chosen in the settings (Factory), like the analyzer."""

from functools import lru_cache

from app.config import Settings, get_settings
from app.reports.base import SummaryWriter
from app.reports.fake import FakeSummaryWriter
from app.reports.fallback import FallbackSummaryWriter
from app.reports.gemini import GeminiSummaryWriter


def build_gemini_writer(settings: Settings) -> SummaryWriter:
    """The main model; when there is a different backup model, it is asked when the main one is busy."""
    main = GeminiSummaryWriter(settings.gemini_api_key, settings.gemini_model)
    backup = settings.gemini_fallback_model
    if not backup or backup == settings.gemini_model:
        return main
    return FallbackSummaryWriter(main, GeminiSummaryWriter(settings.gemini_api_key, backup))


@lru_cache
def get_summary_writer() -> SummaryWriter:
    settings = get_settings()
    if settings.analyzer == "fake":
        return FakeSummaryWriter()
    return build_gemini_writer(settings)
