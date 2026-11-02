"""How long the service has been running, shown by /health."""

import time
from collections.abc import Callable

STARTED_AT = time.monotonic()


def uptime_seconds(now: Callable[[], float] = time.monotonic, started_at: float = STARTED_AT) -> int:
    """Whole seconds since the service started."""
    return max(0, int(now() - started_at))
