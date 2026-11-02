from tests.conftest import PDF_BYTES, auth


def test_every_answer_has_a_request_id(client):
    response = client.get("/health")
    assert len(response.headers["X-Request-ID"]) == 32


def test_the_request_id_of_the_caller_is_returned(client):
    response = client.get("/health", headers={"X-Request-ID": "backend-42"})
    assert response.headers["X-Request-ID"] == "backend-42"
