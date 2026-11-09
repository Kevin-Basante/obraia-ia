from types import SimpleNamespace

import pytest

from app.analyzers.base import AnalyzerBusyError, AnalyzerError
from app.reports.gemini import GeminiSummaryWriter, parse_summary
from app.reports.prompt import summary_prompt
from app.reports.schemas import RawSummary, SummaryRequest
from tests.report_figures import FULL_FIGURES, body
from tests.test_gemini import FakeModels, api_error


def request(language="es", report_type="public", figures=None):
    return SummaryRequest.model_validate(body(language, report_type, figures))


def writer_with(models) -> GeminiSummaryWriter:
    writer = GeminiSummaryWriter("key", "gemini-test")
    writer._client = SimpleNamespace(models=models)
    return writer


def test_gemini_sends_the_prompt_and_asks_for_json():
    models = FakeModels(SimpleNamespace(parsed=RawSummary(summary="Bien"), text=None))

    answer = writer_with(models).write(request("en", "full", FULL_FIGURES))

    assert answer.summary == "Bien"
    prompt = models.kwargs["contents"][0]
    assert "Write in English" in prompt
    assert '"approved_budget":68645101' in prompt
    assert models.kwargs["config"].response_mime_type == "application/json"


def test_gemini_reads_the_text_when_the_sdk_did_not_parse_it():
    assert parse_summary(None, '{"summary": "Bien", "recommendations": ["Uno"]}').recommendations == ["Uno"]
    with pytest.raises(AnalyzerError):
        parse_summary(None, "not json")


def test_gemini_without_key_fails():
    with pytest.raises(AnalyzerError):
        GeminiSummaryWriter("", "gemini-test").write(request())


def test_gemini_busy_and_other_errors():
    with pytest.raises(AnalyzerBusyError):
        writer_with(FakeModels(error=api_error(503))).write(request())
    with pytest.raises(AnalyzerError) as error:
        writer_with(FakeModels(error=api_error(400, "bad request"))).write(request())
    assert not isinstance(error.value, AnalyzerBusyError)


def test_the_public_prompt_forbids_money():
    public = summary_prompt("es", "public", "{}")
    full = summary_prompt("es", "full", "{}")

    assert "Spanish (Colombia)" in public
    assert "never mention budgets" in public
    assert "never mention budgets" not in full
    assert "approved budget" in full
