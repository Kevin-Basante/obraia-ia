"""Steps that run after cleaning."""

from app.elements import ElementType
from app.postprocess.base import Pipeline, Report
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
