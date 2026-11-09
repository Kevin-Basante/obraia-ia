"""Decorator that asks a backup writer when the main model is busy."""

import logging

from app.analyzers.base import AnalyzerBusyError
from app.reports.base import SummaryWriter
from app.reports.schemas import RawSummary, SummaryRequest

logger = logging.getLogger(__name__)


class FallbackSummaryWriter:
    """Wraps the main writer (Decorator pattern). There are no waits between tries:
    the backend gives the whole summary less than a minute."""

    def __init__(self, main: SummaryWriter, backup: SummaryWriter):
        self.main = main
        self.backup = backup

    @property
    def model_name(self) -> str:
        return self.main.model_name

    def ready(self) -> bool:
        return self.main.ready()

    def write(self, request: SummaryRequest) -> RawSummary:
        try:
            return self.main.write(request)
        except AnalyzerBusyError as ex:
            logger.warning(
                "%s is busy (%s), writing the summary with %s", self.main.model_name, ex, self.backup.model_name
            )
        return self.backup.write(request)
