from app.request_id import current_request_id, pick_request_id, reset_request_id, set_request_id


def test_keeps_a_valid_incoming_id():
    assert pick_request_id("abc-123_X") == "abc-123_X"


def test_creates_an_id_when_none_comes():
    first = pick_request_id(None)
    assert len(first) == 32
    assert first != pick_request_id(None)


def test_replaces_an_invalid_id():
    for value in ["", "has space", "x" * 65, "line\nbreak"]:
        assert pick_request_id(value) != value


def test_current_id_lives_only_inside_the_request():
    assert current_request_id() == "-"
    token = set_request_id("req-1")
    assert current_request_id() == "req-1"
    reset_request_id(token)
    assert current_request_id() == "-"
