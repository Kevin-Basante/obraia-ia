from types import SimpleNamespace

import pytest
from google.genai import errors

from app.analyzers.base import AnalyzerError
from app.analyzers.gemini import GeminiAnalyzer, parse_answer
from app.schemas import RawAnalysis, RawMeasurement


class FakeModels:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.kwargs = None

    def generate_content(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return self.response


def analyzer_with(models) -> GeminiAnalyzer:
    analyzer = GeminiAnalyzer("key", "gemini-test")
    analyzer._client = SimpleNamespace(models=models)
    return analyzer


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
    error = errors.ClientError(429, {"error": {"code": 429, "message": "quota", "status": "RESOURCE_EXHAUSTED"}})
    with pytest.raises(AnalyzerError, match="429"):
        analyzer_with(FakeModels(error=error)).analyze(b"%PDF-", "application/pdf", 1)


def test_parse_answer_reads_the_text_when_not_parsed():
    result = parse_answer(None, '{"measurements": [{"element_type": "roof", "length_m": 9, "width_m": 8}]}')
    assert result.measurements[0].element_type == "roof"
    assert result.warnings == []


def test_parse_answer_rejects_invalid_json():
    with pytest.raises(AnalyzerError):
        parse_answer(None, "not json")
    with pytest.raises(AnalyzerError):
        parse_answer(None, None)
