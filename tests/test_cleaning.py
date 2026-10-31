from app.cleaning import parse_element
from app.elements import ElementType


def test_parse_element_accepts_case_and_spaces():
    assert parse_element(" WALL ") == ElementType.WALL


def test_parse_element_accepts_plural_names():
    assert parse_element("Walls") == ElementType.WALL
    assert parse_element("footing") == ElementType.FOUNDATION


def test_parse_element_returns_none_for_unknown_names():
    assert parse_element("window") is None
