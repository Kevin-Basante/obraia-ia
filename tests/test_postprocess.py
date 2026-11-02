"""Steps that run after cleaning."""

from app.elements import ElementType
from app.postprocess.base import Pipeline, Report
from app.postprocess.merge import MergeDuplicates
from app.postprocess.plausibility import PlausibilityCheck
from app.postprocess.sorting import SortByFloorAndElement
from app.schemas import ElementMeasurement


def wall(length=3.0, height=2.4, floor=1, quantity=1, notes=None) -> ElementMeasurement:
    return ElementMeasurement(
        element_type=ElementType.WALL, floor_number=floor, length_m=length, height_m=height, quantity=quantity, notes=notes
    )


class Recorder:
    def __init__(self, name, calls):
        self.name = name
        self.calls = calls

    def apply(self, measurements, report):
        self.calls.append(self.name)
        report.warnings.append(self.name)
        return measurements[1:]


def test_steps_run_in_order_and_pass_the_list_along():
    calls = []
    result, report = Pipeline([Recorder("a", calls), Recorder("b", calls)]).run([wall(1), wall(2), wall(3)])
    assert calls == ["a", "b"]
    assert [item.length_m for item in result] == [3]
    assert report.warnings == ["a", "b"]


def test_empty_pipeline_keeps_everything():
    items = [wall()]
    result, report = Pipeline([]).run(items)
    assert result == items
    assert report == Report()


def merge(items):
    report = Report()
    return MergeDuplicates().apply(items, report), report


def test_merges_equal_rows_and_adds_quantities():
    result, report = merge([wall(quantity=2), wall(quantity=3)])
    assert len(result) == 1
    assert result[0].quantity == 5
    assert report.merged == 1


def test_keeps_rows_of_other_floors_or_sizes():
    result, report = merge([wall(), wall(floor=2), wall(length=4)])
    assert len(result) == 3
    assert report.merged == 0


def test_joins_different_notes_once():
    result, _ = merge([wall(notes="Fachada"), wall(notes="Patio"), wall(notes="Patio")])
    assert result[0].notes == "Fachada; Patio"


def test_keeps_the_note_when_only_one_row_has_it():
    result, _ = merge([wall(), wall(notes="Patio")])
    assert result[0].notes == "Patio"


def test_quantity_never_goes_over_the_limit():
    result, _ = merge([wall(quantity=900), wall(quantity=900)])
    assert result[0].quantity == 1000


def test_merge_does_not_change_the_original_rows():
    first = wall(quantity=2)
    merge([first, wall()])
    assert first.quantity == 2


def check(items):
    report = Report()
    return PlausibilityCheck().apply(items, report), report


def test_normal_sizes_have_no_warning():
    result, report = check([wall()])
    assert len(result) == 1
    assert report.warnings == []


def test_warns_about_a_very_tall_wall_and_keeps_it():
    result, report = check([wall(height=9)])
    assert len(result) == 1
    assert report.warnings == ["Check the wall on floor 1: its height of 9 m is unusual (more than 6 m)"]


def test_one_warning_per_strange_dimension():
    slab = ElementMeasurement(element_type=ElementType.SLAB, floor_number=2, length_m=50, width_m=8, height_m=0.8)
    _, report = check([slab])
    assert len(report.warnings) == 2
    assert all("slab on floor 2" in warning for warning in report.warnings)


def test_every_element_has_plausible_maximums_for_its_dimensions():
    from app.elements import PLAUSIBLE_MAXIMUMS, REQUIRED_DIMENSIONS

    for element, dimensions in REQUIRED_DIMENSIONS.items():
        assert set(PLAUSIBLE_MAXIMUMS[element]) == set(dimensions)


def roof(floor=1) -> ElementMeasurement:
    return ElementMeasurement(element_type=ElementType.ROOF, floor_number=floor, length_m=9, width_m=8)


def test_sorts_by_floor_then_build_order():
    items = [roof(2), wall(floor=2), roof(1), wall(length=5)]
    result = SortByFloorAndElement().apply(items, Report())
    assert [(item.floor_number, item.element_type.value) for item in result] == [
        (1, "wall"),
        (1, "roof"),
        (2, "wall"),
        (2, "roof"),
    ]


def test_sorting_keeps_the_model_order_inside_a_group():
    result = SortByFloorAndElement().apply([wall(length=7), wall(length=2)], Report())
    assert [item.length_m for item in result] == [7, 2]
