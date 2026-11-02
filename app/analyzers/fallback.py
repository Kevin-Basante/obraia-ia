"""Decorator that sends the blueprint to a backup analyzer when the main one stays busy."""

import logging

from app.analyzers.base import AnalyzerBusyError, BlueprintAnalyzer
from app.schemas import RawAnalysis

logger = logging.getLogger(__name__)


class FallbackAnalyzer:
    """Wraps the main analyzer (Decorator pattern); when it is busy, the backup reads the blueprint.

    The answer of the backup carries a warning, so the user knows a lighter model read it.
    """

    def __init__(self, main: BlueprintAnalyzer, backup: BlueprintAnalyzer):
        self.main = main
        self.backup = backup

    @property
    def model_name(self) -> str:
        return self.main.model_name

    def ready(self) -> bool:
        return self.main.ready()

    def analyze(self, content: bytes, mime_type: str, floors: int) -> RawAnalysis:
        try:
            return self.main.analyze(content, mime_type, floors)
        except AnalyzerBusyError as ex:
            logger.warning("%s stays busy (%s), using %s", self.main.model_name, ex, self.backup.model_name)
        result = self.backup.analyze(content, mime_type, floors)
        note = f"The backup model {self.backup.model_name} read this blueprint because {self.main.model_name} was busy"
        result.warnings = [*result.warnings, note]
        return result
