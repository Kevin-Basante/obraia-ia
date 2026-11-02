"""Totals per element type of an analysis."""

from app.elements import ElementType
from app.quantities import quantity_of, unit_of
from app.schemas import ElementMeasurement, ElementSummary


def summarize(measurements: list[ElementMeasurement]) -> list[ElementSummary]:
    """One line per element type found, in the order of ElementType."""
    lines = []
    for element in ElementType:
        items = [item for item in measurements if item.element_type == element]
        if not items:
            continue
        lines.append(
            ElementSummary(
                element_type=element,
                rows=len(items),
                pieces=sum(item.quantity for item in items),
                total=round(sum(quantity_of(item) for item in items), 2),
                unit=unit_of(element),
            )
        )
    return lines
