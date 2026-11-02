from tests.conftest import auth


def test_lists_every_element_with_its_dimensions(client):
    response = client.get("/api/v1/elements", headers=auth())
    assert response.status_code == 200
    body = response.json()
    assert [item["element_type"] for item in body] == ["foundation", "column", "beam", "slab", "wall", "floor", "roof"]
    wall = body[4]
    assert wall == {"element_type": "wall", "required_dimensions": ["length_m", "height_m"], "unit": "m2"}


def test_elements_need_the_service_token(client):
    assert client.get("/api/v1/elements").status_code == 401
