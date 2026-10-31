import pytest

from tests.conftest import PDF_BYTES, make_settings


def post(client, headers=None):
    return client.post(
        "/api/v1/blueprints/analyze",
        files={"file": ("plan.pdf", PDF_BYTES, "application/pdf")},
        headers=headers or {},
    )


def test_rejects_missing_token(client):
    response = post(client)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_SERVICE_TOKEN"


def test_rejects_wrong_token(client):
    assert post(client, {"X-Service-Token": "wrong"}).status_code == 401


@pytest.mark.parametrize("settings", [make_settings(service_token="")])
def test_refuses_to_work_without_a_configured_token(client):
    response = post(client, {"X-Service-Token": "anything"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SERVICE_NOT_CONFIGURED"
