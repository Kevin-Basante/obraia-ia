from app.cleaning import clean_measurement, clean_measurements, parse_element
from app.elements import ElementType
from app.schemas import RawMeasurement


def raw(**values) -> RawMeasurement:
    return RawMeasurement(**values)


def test_parse_element_accepts_case_and_spaces():
    assert parse_element(" WALL ") == ElementType.WALL


def test_parse_element_accepts_plural_names():
    assert parse_element("Walls") == ElementType.WALL
    assert parse_element("footing") == ElementType.FOUNDATION


def test_parse_element_returns_none_for_unknown_names():
    assert parse_element("window") is None


def test_keeps_a_valid_wall():
    result = clean_measurement(raw(element_type="wall", floor_number=1, length_m=10, height_m=2.4, quantity=2), 1)
    assert result.element_type == ElementType.WALL
    assert result.length_m == 10
    assert result.height_m == 2.4
    assert result.quantity == 2


def test_drops_dimensions_the_element_does_not_use():
    result = clean_measurement(raw(element_type="wall", length_m=10, width_m=0.15, height_m=2.4), 1)
    assert result.width_m is None


def test_rounds_dimensions_to_centimeters():
    result = clean_measurement(raw(element_type="floor", length_m=4.567, width_m=3.123), 1)
    assert result.length_m == 4.57
    assert result.width_m == 3.12


def test_discards_missing_required_dimension():
    assert clean_measurement(raw(element_type="slab", length_m=9, width_m=8), 1) is None


def test_discards_zero_or_negative_dimension():
    assert clean_measurement(raw(element_type="roof", length_m=9, width_m=0), 1) is None
    assert clean_measurement(raw(element_type="roof", length_m=-1, width_m=8), 1) is None


def test_discards_unknown_element():
    assert clean_measurement(raw(element_type="door", length_m=1, width_m=1), 1) is None


def test_discards_floor_the_project_does_not_have():
    assert clean_measurement(raw(element_type="floor", floor_number=2, length_m=5, width_m=4), 1) is None


def test_missing_floor_and_quantity_default_to_one():
    result = clean_measurement(raw(element_type="floor", length_m=5, width_m=4), 2)
    assert result.floor_number == 1
    assert result.quantity == 1


def test_discards_values_out_of_range():
    assert clean_measurement(raw(element_type="floor", length_m=5000, width_m=4), 1) is None
    assert clean_measurement(raw(element_type="floor", length_m=5, width_m=4, quantity=5000), 1) is None


def test_trims_notes_and_empties_become_none():
    assert clean_measurement(raw(element_type="floor", length_m=5, width_m=4, notes="   "), 1).notes is None
    long_notes = clean_measurement(raw(element_type="floor", length_m=5, width_m=4, notes="x" * 600), 1).notes
    assert len(long_notes) == 500


def test_clean_measurements_counts_discarded():
    valid, discarded = clean_measurements(
        [raw(element_type="floor", length_m=5, width_m=4), raw(element_type="door", length_m=1)], 1
    )
    assert len(valid) == 1
    assert discarded == 1
