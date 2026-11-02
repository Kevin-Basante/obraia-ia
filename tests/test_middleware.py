from tests.conftest import PDF_BYTES, auth


def test_every_answer_has_a_request_id(client):
    response = client.get("/health")
    assert len(response.headers["X-Request-ID"]) == 32


def test_the_request_id_of_the_caller_is_returned(client):
    response = client.get("/health", headers={"X-Request-ID": "backend-42"})
    assert response.headers["X-Request-ID"] == "backend-42"


def test_an_invalid_request_id_is_replaced(client):
    response = client.get("/health", headers={"X-Request-ID": "not valid!"})
    assert response.headers["X-Request-ID"] != "not valid!"


def test_errors_carry_the_request_id_too(client):
    response = client.post("/api/v1/blueprints/analyze", files={"file": ("plan.pdf", PDF_BYTES)})
    assert response.status_code == 401
    assert "X-Request-ID" in response.headers


def test_analysis_answers_carry_the_request_id(client):
    response = client.post(
        "/api/v1/blueprints/analyze",
        files={"file": ("plan.pdf", PDF_BYTES)},
        headers={**auth(), "X-Request-ID": "analysis-1"},
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "analysis-1"


def test_requests_are_written_to_the_access_log(client, caplog):
    caplog.set_level("INFO", logger="app.access")
    client.get("/openapi.json")
    assert any("GET /openapi.json -> 200" in line for line in caplog.messages)


def test_health_checks_are_not_logged(client, caplog):
    caplog.set_level("INFO", logger="app.access")
    client.get("/health")
    assert [item for item in caplog.records if item.name == "app.access"] == []
