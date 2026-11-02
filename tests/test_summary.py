from app.elements import ElementType
from app.schemas import ElementMeasurement
from app.summary import summarize


def wall(length, quantity=1) -> ElementMeasurement:
    return ElementMeasurement(element_type="wall", floor_number=1, length_m=length, height_m=2.5, quantity=quantity)


def slab() -> ElementMeasurement:
    return ElementMeasurement(element_type="slab", floor_number=1, length_m=9, width_m=8, height_m=0.1)


def test_empty_analysis_has_no_lines():
    assert summarize([]) == []


def test_adds_rows_pieces_and_totals_per_element():
    lines = summarize([wall(4, 2), wall(2), slab()])
    assert [line.element_type for line in lines] == [ElementType.SLAB, ElementType.WALL]
    walls = lines[1]
    assert (walls.rows, walls.pieces, walls.total, walls.unit) == (2, 3, 25.0, "m2")
    assert (lines[0].total, lines[0].unit) == (7.2, "m3")
