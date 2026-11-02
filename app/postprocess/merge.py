"""Joins rows that describe the same element, so the user does not see it twice."""

from app.postprocess.base import Report
from app.schemas import ElementMeasurement


def _key(item: ElementMeasurement) -> tuple:
    return (item.element_type, item.floor_number, item.length_m, item.width_m, item.height_m)


class MergeDuplicates:
    """Rows with the same element, floor and dimensions become one row with the quantities added."""

    def apply(self, measurements: list[ElementMeasurement], report: Report) -> list[ElementMeasurement]:
        merged: dict[tuple, ElementMeasurement] = {}
        for item in measurements:
            key = _key(item)
            if key not in merged:
                merged[key] = item.model_copy()
                continue
            current = merged[key]
            current.quantity = min(1000, current.quantity + item.quantity)
            current.notes = _join_notes(current.notes, item.notes)
            report.merged += 1
        return list(merged.values())


def _join_notes(first: str | None, second: str | None) -> str | None:
    if not second or second == first:
        return first
    if not first:
        return second
    return f"{first}; {second}"[:500]
