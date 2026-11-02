import pytest

from app.elements import ElementType
from app.quantities import quantity_of, unit_of
from app.schemas import ElementMeasurement


def item(element, quantity=1, **dims) -> ElementMeasurement:
    return ElementMeasurement(element_type=element, floor_number=1, quantity=quantity, **dims)


@pytest.mark.parametrize(
    ("element", "unit"),
    [("foundation", "m3"), ("column", "m3"), ("beam", "m3"), ("slab", "m3"), ("wall", "m2"), ("floor", "m2"), ("roof", "m2")],
)
def test_units(element, unit):
    assert unit_of(ElementType(element)) == unit


def test_concrete_is_a_volume():
    assert quantity_of(item(ElementType.COLUMN, 4, length_m=0.3, width_m=0.3, height_m=2.5)) == 0.9


def test_wall_is_length_by_height():
    assert quantity_of(item(ElementType.WALL, 2, length_m=3.5, height_m=2.4)) == 16.8


def test_roof_is_length_by_width():
    assert quantity_of(item(ElementType.ROOF, length_m=9, width_m=8)) == 72
