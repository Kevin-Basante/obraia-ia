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
