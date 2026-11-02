"""Limits how many blueprints are analyzed at the same time."""

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from app.config import get_settings
from app.errors import ServiceError


class AnalysisLimiter:
    """Hands out a fixed number of slots; when none is free, the request is refused instead of waiting."""

    def __init__(self, slots: int):
        self.slots = slots
        self._in_use = 0
        self._lock = threading.Lock()

    @property
    def in_use(self) -> int:
        return self._in_use

    def try_acquire(self) -> bool:
        with self._lock:
            if self._in_use >= self.slots:
                return False
            self._in_use += 1
            return True

    def release(self) -> None:
        with self._lock:
            self._in_use = max(0, self._in_use - 1)

    @contextmanager
    def slot(self) -> Iterator[None]:
        """Holds a slot while the block runs; raises ANALYZER_BUSY when all are taken."""
        if not self.try_acquire():
            raise ServiceError(503, "ANALYZER_BUSY", "Too many blueprints are being analyzed. Try again in a minute")
        try:
            yield
        finally:
            self.release()


@lru_cache
def get_limiter() -> AnalysisLimiter:
    return AnalysisLimiter(get_settings().max_concurrent_analyses)
