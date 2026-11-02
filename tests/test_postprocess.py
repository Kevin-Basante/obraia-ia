"""Steps that run after cleaning."""

from app.elements import ElementType
from app.postprocess.base import Pipeline, Report
from app.postprocess.merge import MergeDuplicates
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
