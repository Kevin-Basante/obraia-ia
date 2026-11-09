"""Common interface of the summary writers (Strategy pattern): the route does not know which one runs."""

from typing import Protocol

from app.reports.schemas import RawSummary, SummaryRequest


class SummaryWriter(Protocol):
    """Writes a short summary with recommendations from the figures of a report."""

    model_name: str

    def ready(self) -> bool:
        """True when the writer has everything it needs (for example, its API key)."""
        ...

    def write(self, request: SummaryRequest) -> RawSummary: ...
