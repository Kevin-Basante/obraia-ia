from tests.conftest import make_settings


def test_health_is_public_and_reports_the_analyzer(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP", "analyzer": "fake", "model": "fake", "ready": True}


def test_docs_are_available(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").json()["info"]["title"] == "ObraIA AI service"


def test_settings_max_file_bytes():
    assert make_settings(max_file_mb=2).max_file_bytes == 2 * 1024 * 1024
