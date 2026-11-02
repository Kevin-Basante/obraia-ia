from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import PDF_BYTES, auth


class BrokenAnalyzer:
    model_name = "broken"

    def ready(self):
        return True

    def analyze(self, content, mime_type, floors):
        raise RuntimeError("secret detail")


def test_unexpected_errors_keep_the_error_shape(client, caplog):
    from app.analyzers.factory import get_analyzer

    app.dependency_overrides[get_analyzer] = lambda: BrokenAnalyzer()
    response = TestClient(app, raise_server_exceptions=False).post(
        "/api/v1/blueprints/analyze", files={"file": ("plan.pdf", PDF_BYTES)}, headers=auth()
    )
    assert response.status_code == 500
    assert response.json() == {"error": {"code": "INTERNAL_ERROR", "message": "Unexpected error in the AI service"}}
    assert "secret detail" not in response.text
    assert any("Unexpected error" in line for line in caplog.messages)


def test_unknown_routes_answer_not_found(client):
    response = client.get("/api/v1/nothing")
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "NOT_FOUND", "message": "Not Found"}}


def test_wrong_method_answers_method_not_allowed(client):
    response = client.get("/api/v1/blueprints/analyze", headers=auth())
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"
    assert "POST" in response.headers["allow"]


def test_validation_errors_name_the_fields(client):
    response = client.post(
        "/api/v1/blueprints/analyze", files={"file": ("plan.pdf", PDF_BYTES)}, data={"floors": "5"}, headers=auth()
    )
    assert response.status_code == 400
    assert response.json() == {"error": {"code": "VALIDATION_ERROR", "message": "Invalid fields: floors"}}
