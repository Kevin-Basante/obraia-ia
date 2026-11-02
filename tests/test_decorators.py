"""Analyzer decorators: retries and the backup model."""

import pytest

from app.analyzers.base import AnalyzerBusyError, AnalyzerError
from app.analyzers.fallback import FallbackAnalyzer
from app.analyzers.retrying import RetryingAnalyzer
from app.schemas import RawAnalysis, RawMeasurement


class ScriptedAnalyzer:
    """Answers each call with the next item of the script: exceptions are raised."""

    def __init__(self, *script, model_name="main-model", ready=True):
        self.script = list(script)
        self.model_name = model_name
        self.calls = 0
        self._ready = ready

    def ready(self) -> bool:
        return self._ready

    def analyze(self, content, mime_type, floors):
        self.calls += 1
        item = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(item, Exception):
            raise item
        return item


def result(element_type="wall") -> RawAnalysis:
    return RawAnalysis(measurements=[RawMeasurement(element_type=element_type, length_m=3)])


def retrying(inner, retries=2, waits=None):
    return RetryingAnalyzer(inner, retries=retries, retry_delay=1.0, sleep=(waits if waits is not None else []).append)


def test_returns_the_first_answer_without_waiting():
    waits = []
    inner = ScriptedAnalyzer(result())
    assert retrying(inner, waits=waits).analyze(b"", "application/pdf", 1).measurements[0].element_type == "wall"
    assert inner.calls == 1
    assert waits == []


def test_tries_again_while_busy():
    inner = ScriptedAnalyzer(AnalyzerBusyError("busy"), result("roof"))
    assert retrying(inner).analyze(b"", "application/pdf", 1).measurements[0].element_type == "roof"
    assert inner.calls == 2


def test_waits_twice_as_long_each_time():
    waits = []
    inner = ScriptedAnalyzer(AnalyzerBusyError("busy"))
    with pytest.raises(AnalyzerBusyError):
        retrying(inner, retries=3, waits=waits).analyze(b"", "application/pdf", 1)
    assert waits == [1.0, 2.0, 4.0]
    assert inner.calls == 4


def test_other_errors_are_not_repeated():
    inner = ScriptedAnalyzer(AnalyzerError("bad file"), result())
    with pytest.raises(AnalyzerError, match="bad file"):
        retrying(inner).analyze(b"", "application/pdf", 1)
    assert inner.calls == 1


def test_zero_retries_calls_once():
    inner = ScriptedAnalyzer(AnalyzerBusyError("busy"))
    with pytest.raises(AnalyzerBusyError):
        retrying(inner, retries=0).analyze(b"", "application/pdf", 1)
    assert inner.calls == 1


def test_retrying_shows_the_inner_model_and_readiness():
    analyzer = retrying(ScriptedAnalyzer(result(), model_name="m1", ready=False))
    assert analyzer.model_name == "m1"
    assert analyzer.ready() is False


def test_main_answer_has_no_note():
    backup = ScriptedAnalyzer(result("roof"), model_name="lite")
    answer = FallbackAnalyzer(ScriptedAnalyzer(result()), backup).analyze(b"", "application/pdf", 1)
    assert answer.measurements[0].element_type == "wall"
    assert answer.warnings == []
    assert backup.calls == 0


def test_backup_reads_when_the_main_one_is_busy():
    main = ScriptedAnalyzer(AnalyzerBusyError("busy"))
    backup = ScriptedAnalyzer(result("roof"), model_name="lite")
    answer = FallbackAnalyzer(main, backup).analyze(b"", "application/pdf", 1)
    assert answer.measurements[0].element_type == "roof"
    assert answer.warnings == ["The backup model lite read this blueprint because main-model was busy"]
