from types import SimpleNamespace

import pytest
from google.genai import errors

from app.analyzers.base import AnalyzerBusyError, AnalyzerError
from app.analyzers.gemini import GeminiAnalyzer, parse_answer
from app.schemas import RawAnalysis, RawMeasurement


class FakeModels:
    """Answers each call with the next item of answers: an error is raised, anything else returned."""

    def __init__(self, response=None, error=None, answers=None):
        self.answers = list(answers) if answers is not None else [error or response]
        self.kwargs = None
        self.models = []

    def generate_content(self, **kwargs):
        self.kwargs = kwargs
        self.models.append(kwargs["model"])
        answer = self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]
        if isinstance(answer, Exception):
            raise answer
        return answer


def analyzer_with(models, **options) -> GeminiAnalyzer:
    analyzer = GeminiAnalyzer("key", "gemini-test", sleep=lambda seconds: None, **options)
    analyzer._client = SimpleNamespace(models=models)
    return analyzer


def api_error(code: int, message: str = "busy") -> errors.APIError:
    error_class = errors.ClientError if code < 500 else errors.ServerError
    return error_class(code, {"error": {"code": code, "message": message, "status": "UNAVAILABLE"}})


def answer(element_type: str = "wall"):
    parsed = RawAnalysis(measurements=[RawMeasurement(element_type=element_type, length_m=3)])
    return SimpleNamespace(parsed=parsed, text=None)


def test_is_not_ready_without_key():
    assert GeminiAnalyzer("", "gemini-test").ready() is False


def test_refuses_to_analyze_without_key():
    with pytest.raises(AnalyzerError):
        GeminiAnalyzer("", "gemini-test").analyze(b"%PDF-", "application/pdf", 1)


def test_sends_file_prompt_and_json_schema():
    parsed = RawAnalysis(measurements=[RawMeasurement(element_type="wall", length_m=3, height_m=2.4)])
    models = FakeModels(SimpleNamespace(parsed=parsed, text=None))
    result = analyzer_with(models).analyze(b"%PDF-1.7", "application/pdf", 2)
    assert result is parsed
    assert models.kwargs["model"] == "gemini-test"
    part, prompt = models.kwargs["contents"]
    assert part.inline_data.mime_type == "application/pdf"
    assert part.inline_data.data == b"%PDF-1.7"
    assert "2 floor(s)" in prompt
    config = models.kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_schema is RawAnalysis
    assert config.temperature == 0


def test_translates_api_errors():
    with pytest.raises(AnalyzerError, match="400: bad file") as raised:
        analyzer_with(FakeModels(error=api_error(400, "bad file"))).analyze(b"%PDF-", "application/pdf", 1)
    assert not isinstance(raised.value, AnalyzerBusyError)


def test_other_errors_are_not_retried():
    models = FakeModels(answers=[api_error(400), answer()])
    with pytest.raises(AnalyzerError):
        analyzer_with(models, retries=2).analyze(b"%PDF-", "application/pdf", 1)
    assert models.models == ["gemini-test"]


@pytest.mark.parametrize("code", [429, 500, 503, 504])
def test_busy_answers_are_retried(code):
    models = FakeModels(answers=[api_error(code), answer("roof")])
    result = analyzer_with(models, retries=2).analyze(b"%PDF-", "application/pdf", 1)
    assert result.measurements[0].element_type == "roof"
    assert models.models == ["gemini-test", "gemini-test"]


def test_busy_after_all_retries():
    models = FakeModels(error=api_error(503))
    with pytest.raises(AnalyzerBusyError, match="answered 503"):
        analyzer_with(models, retries=2).analyze(b"%PDF-", "application/pdf", 1)
    assert models.models == ["gemini-test"] * 3


def test_waits_longer_before_each_retry():
    waits = []
    analyzer = GeminiAnalyzer("key", "gemini-test", retries=2, retry_delay=1.5, sleep=waits.append)
    analyzer._client = SimpleNamespace(models=FakeModels(error=api_error(503)))
    with pytest.raises(AnalyzerBusyError):
        analyzer.analyze(b"%PDF-", "application/pdf", 1)
    assert waits == [1.5, 3.0]


def test_parse_answer_reads_the_text_when_not_parsed():
    result = parse_answer(None, '{"measurements": [{"element_type": "roof", "length_m": 9, "width_m": 8}]}')
    assert result.measurements[0].element_type == "roof"
    assert result.warnings == []


def test_parse_answer_rejects_invalid_json():
    with pytest.raises(AnalyzerError):
        parse_answer(None, "not json")
    with pytest.raises(AnalyzerError):
        parse_answer(None, None)
