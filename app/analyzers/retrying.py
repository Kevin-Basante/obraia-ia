"""Decorator that tries the same analyzer again while the model is busy."""

import logging
import time
from collections.abc import Callable

from app.analyzers.base import AnalyzerBusyError, BlueprintAnalyzer
from app.schemas import RawAnalysis

logger = logging.getLogger(__name__)


class RetryingAnalyzer:
    """Wraps an analyzer (Decorator pattern) and repeats the call when it raises AnalyzerBusyError.

    It waits retry_delay seconds before the first new try and doubles the wait each time:
    a short spike of demand has time to pass. Other errors are not repeated.
    """

    def __init__(
        self,
        inner: BlueprintAnalyzer,
        retries: int,
        retry_delay: float = 2.0,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.inner = inner
        self.retries = retries
        self.retry_delay = retry_delay
        self._sleep = sleep

    @property
    def model_name(self) -> str:
        return self.inner.model_name

    def ready(self) -> bool:
        return self.inner.ready()

    def analyze(self, content: bytes, mime_type: str, floors: int) -> RawAnalysis:
        for attempt in range(self.retries):
            try:
                return self.inner.analyze(content, mime_type, floors)
            except AnalyzerBusyError as ex:
                logger.warning("%s is busy (%s), try %d", self.model_name, ex, attempt + 1)
                self._sleep(self.retry_delay * 2**attempt)
        return self.inner.analyze(content, mime_type, floors)
