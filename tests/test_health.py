from app import __version__
from tests.conftest import make_settings


def test_health_is_public_and_reports_the_analyzer(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert {key: body[key] for key in ("status", "analyzer", "model", "ready")} == {
        "status": "UP",
        "analyzer": "fake",
        "model": "fake",
        "ready": True,
    }


def test_docs_are_available(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").json()["info"]["title"] == "ObraIA AI service"


def test_settings_max_file_bytes():
    assert make_settings(max_file_mb=2).max_file_bytes == 2 * 1024 * 1024


def test_docs_show_the_service_version(client):
    assert client.get("/openapi.json").json()["info"]["version"] == __version__


def test_health_reports_version_and_uptime(client):
    body = client.get("/health").json()
    assert body["version"] == __version__
    assert body["uptime_seconds"] >= 0


def test_docs_describe_each_group_of_routes(client):
    tags = [tag["name"] for tag in client.get("/openapi.json").json()["tags"]]
    assert tags == ["Health", "Blueprints", "Elements"]


def test_docs_show_an_example_answer(client):
    schema = client.get("/openapi.json").json()["components"]["schemas"]["AnalysisResponse"]
    example = schema["examples"][0]
    assert example["measurements"][0]["element_type"] == "wall"
    assert example["summary"][0]["unit"] == "m2"
