from app.analyzers.base import AnalyzerBusyError, AnalyzerError
from app.analyzers.factory import get_analyzer
from app.main import app
from app.schemas import RawAnalysis, RawMeasurement
from tests.conftest import PDF_BYTES, auth


class StubAnalyzer:
    model_name = "stub"

    def __init__(self, answer=None, error=None, ready=True):
        self.answer = answer
        self.error = error
        self._ready = ready
        self.calls = []

    def ready(self):
        return self._ready

    def analyze(self, content, mime_type, floors):
        self.calls.append((content, mime_type, floors))
        if self.error:
            raise self.error
        return self.answer


def use(analyzer):
    app.dependency_overrides[get_analyzer] = lambda: analyzer
    return analyzer


def analyze(client, content=PDF_BYTES, floors=None):
    data = {} if floors is None else {"floors": str(floors)}
    return client.post(
        "/api/v1/blueprints/analyze",
        files={"file": ("plan.pdf", content, "application/pdf")},
        data=data,
        headers=auth(),
    )


def mixed_answer():
    return RawAnalysis(
        measurements=[
            RawMeasurement(element_type="Walls", floor_number=1, length_m=12.345, height_m=2.4, quantity=3),
            RawMeasurement(element_type="window", length_m=1.2, width_m=1.0),
            RawMeasurement(element_type="slab", floor_number=2, length_m=9, width_m=8, height_m=0.12),
        ],
        warnings=["Escala no visible"],
    )


def test_returns_the_fake_measurements(client):
    response = analyze(client)
    assert response.status_code == 200
    body = response.json()
    assert body["model"] == "fake"
    assert body["discarded"] == 0
    assert [m["element_type"] for m in body["measurements"]] == ["foundation", "slab", "wall", "roof"]
    assert body["warnings"]


def test_cleans_the_answer_and_counts_discarded(client):
    use(StubAnalyzer(answer=mixed_answer()))
    body = analyze(client).json()
    assert body["discarded"] == 2
    assert body["warnings"] == ["Escala no visible"]
    wall = body["measurements"][0]
    assert wall["element_type"] == "wall"
    assert wall["length_m"] == 12.35
    assert wall["quantity"] == 3
    assert wall["width_m"] is None


def test_second_floor_is_kept_for_two_floor_projects(client):
    use(StubAnalyzer(answer=mixed_answer()))
    body = analyze(client, floors=2).json()
    assert body["discarded"] == 1
    assert body["measurements"][1]["floor_number"] == 2


def test_passes_file_type_and_floors_to_the_analyzer(client):
    stub = use(StubAnalyzer(answer=RawAnalysis(measurements=[])))
    analyze(client, floors=2)
    assert stub.calls == [(PDF_BYTES, "application/pdf", 2)]


def test_detects_the_type_from_the_content_not_the_name(client):
    stub = use(StubAnalyzer(answer=RawAnalysis(measurements=[])))
    analyze(client, content=b"\x89PNG\r\n\x1a\nimage")
    assert stub.calls[0][1] == "image/png"


def test_reports_the_elapsed_time(client):
    body = analyze(client).json()
    assert body["elapsed_ms"] >= 0


def test_rejects_empty_file(client):
    response = analyze(client, content=b"")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_FILE"


def test_rejects_unsupported_file(client):
    response = analyze(client, content=b"PK\x03\x04 zip")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE"


def test_rejects_file_larger_than_the_limit(client):
    response = analyze(client, content=b"%PDF-" + b"0" * (1024 * 1024))
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_rejects_floors_out_of_range(client):
    response = analyze(client, floors=3)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "floors" in response.json()["error"]["message"]


def test_rejects_missing_file(client):
    response = client.post("/api/v1/blueprints/analyze", headers=auth())
    assert response.status_code == 400
    assert "file" in response.json()["error"]["message"]


def test_answers_503_when_the_analyzer_has_no_key(client):
    use(StubAnalyzer(ready=False))
    response = analyze(client)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ANALYZER_NOT_READY"


def test_answers_502_when_the_model_fails(client):
    use(StubAnalyzer(error=AnalyzerError("Gemini answered 429: quota")))
    response = analyze(client)
    assert response.status_code == 502
    assert response.json()["error"] == {"code": "ANALYZER_FAILED", "message": "Gemini answered 429: quota"}


def test_answers_503_when_the_model_is_busy(client):
    use(StubAnalyzer(error=AnalyzerBusyError("Gemini is busy right now. Try again in a few minutes")))
    response = analyze(client)
    assert response.status_code == 503
    assert response.json()["error"] == {
        "code": "ANALYZER_BUSY",
        "message": "Gemini is busy right now. Try again in a few minutes",
    }


def test_failures_are_logged(client, caplog):
    use(StubAnalyzer(error=AnalyzerError("Gemini answered 400: bad file")))
    with caplog.at_level("WARNING"):
        analyze(client)
    assert "plan.pdf" in caplog.text
    assert "Gemini answered 400: bad file" in caplog.text


def pdf_with_pages(pages: int) -> bytes:
    return b"%PDF-1.7\n" + b"<< /Type /Page >>\n" * pages


def test_rejects_a_pdf_with_too_many_pages(client):
    response = client.post("/api/v1/blueprints/analyze", files={"file": ("book.pdf", pdf_with_pages(11))}, headers=auth())
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "PDF_TOO_MANY_PAGES"


def test_accepts_a_pdf_at_the_page_limit(client):
    response = client.post("/api/v1/blueprints/analyze", files={"file": ("plan.pdf", pdf_with_pages(10))}, headers=auth())
    assert response.status_code == 200
