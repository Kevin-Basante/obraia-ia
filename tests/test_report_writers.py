from types import SimpleNamespace

import pytest

from app.analyzers.base import AnalyzerBusyError, AnalyzerError
from app.reports.fake import FakeSummaryWriter
from app.reports.fallback import FallbackSummaryWriter
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


class Writer:
    def __init__(self, name, error=None):
        self.model_name = name
        self.error = error
        self.calls = 0

    def ready(self):
        return True

    def write(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        return RawSummary(summary=f"by {self.model_name}")


def test_the_backup_writes_when_the_main_model_is_busy():
    main, backup = Writer("main", AnalyzerBusyError("busy")), Writer("backup")

    answer = FallbackSummaryWriter(main, backup).write(request())

    assert answer.summary == "by backup"
    assert FallbackSummaryWriter(main, backup).model_name == "main"


def test_other_errors_do_not_go_to_the_backup():
    main, backup = Writer("main", AnalyzerError("bad")), Writer("backup")

    with pytest.raises(AnalyzerError):
        FallbackSummaryWriter(main, backup).write(request())
    assert backup.calls == 0


def test_the_fake_writer_uses_colombian_numbers():
    answer = FakeSummaryWriter().write(request("en", "full", FULL_FIGURES))

    assert "36,4% done" in answer.summary
    assert "$ 270.300.000 of $ 68.645.101" in answer.summary
    assert len(answer.recommendations) == 3
