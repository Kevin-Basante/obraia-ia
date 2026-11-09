from app.main import app
from app.reports.factory import get_summary_writer
from app.reports.schemas import MAX_RECOMMENDATIONS, MAX_SUMMARY_CHARS, RawSummary
from tests.conftest import auth
from tests.report_figures import FULL_FIGURES, body

PATH = "/api/v1/reports/summary"


class StubWriter:
    model_name = "stub"

    def __init__(self, answer=None, error=None, ready=True):
        self.answer = answer
        self.error = error
        self._ready = ready
        self.requests = []

    def ready(self):
        return self._ready

    def write(self, request):
        self.requests.append(request)
        if self.error:
            raise self.error
        return self.answer


def use(writer):
    app.dependency_overrides[get_summary_writer] = lambda: writer
    return writer


def test_needs_the_service_token(client):
    response = client.post(PATH, json=body())

    assert response.status_code == 401


def test_writes_the_summary_in_the_language_of_the_report(client):
    spanish = client.post(PATH, json=body("es"), headers=auth())
    english = client.post(PATH, json=body("en"), headers=auth())

    assert spanish.status_code == 200
    assert spanish.json()["summary"].startswith("La obra Casa Basante va en el 36,4%")
    assert spanish.json()["model"] == "fake"
    assert english.json()["summary"].startswith("Casa Basante is 36,4% done")


def test_the_public_summary_does_not_talk_about_money(client):
    public = client.post(PATH, json=body("es", "public"), headers=auth()).json()
    full = client.post(PATH, json=body("es", "full", FULL_FIGURES), headers=auth()).json()

    assert "$" not in public["summary"]
    assert "$ 270.300.000 de $ 68.645.101" in full["summary"]
    assert "crítico" not in public["summary"] and "El riesgo es crítico" in full["summary"]


def test_sends_the_figures_to_the_writer(client):
    writer = use(StubWriter(RawSummary(summary="Bien", recommendations=["Seguir"])))

    client.post(PATH, json=body("en", "full", FULL_FIGURES), headers=auth())

    request = writer.requests[0]
    assert request.language == "en"
    assert request.report_type == "full"
    assert request.figures.money.approved_budget == 68645101
    assert request.figures.risk.factors[0].code == "schedule_delay"


def test_cleans_the_answer_of_the_model(client):
    long_text = "palabra " * 400
    lines = ["  Uno  ", "", "Dos", "Tres", "Cuatro", "Cinco"]
    use(StubWriter(RawSummary(summary=long_text, recommendations=lines)))

    answer = client.post(PATH, json=body(), headers=auth()).json()

    assert len(answer["summary"]) <= MAX_SUMMARY_CHARS
    assert answer["summary"].endswith("…")
    assert answer["recommendations"] == ["Uno", "Dos", "Tres", "Cuatro"][:MAX_RECOMMENDATIONS]


def test_an_empty_summary_is_a_failure(client):
    use(StubWriter(RawSummary(summary="   ", recommendations=[])))

    response = client.post(PATH, json=body(), headers=auth())

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "ANALYZER_FAILED"
