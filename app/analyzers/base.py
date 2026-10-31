"""Common interface of the analyzers (Strategy pattern): the route does not know which one runs."""

from typing import Protocol

from app.schemas import RawAnalysis


class AnalyzerError(Exception):
    """The model could not be reached or its answer could not be read."""


class AnalyzerBusyError(AnalyzerError):
    """The model is overloaded or out of quota for now; the same request may work a bit later."""


class BlueprintAnalyzer(Protocol):
    """Reads a blueprint file and returns the elements it finds, before cleaning."""

    model_name: str

    def ready(self) -> bool:
        """True when the analyzer has everything it needs (for example, its API key)."""
        ...

    def analyze(self, content: bytes, mime_type: str, floors: int) -> RawAnalysis: ...
