"""Warns about sizes that are possible to read but strange for a house."""

from app.elements import PLAUSIBLE_MAXIMUMS
from app.postprocess.base import Report
from app.schemas import ElementMeasurement

_LABELS = {"length_m": "length", "width_m": "width", "height_m": "height"}


class PlausibilityCheck:
    """Keeps every row and adds a warning for each dimension over its plausible maximum."""

    def apply(self, measurements: list[ElementMeasurement], report: Report) -> list[ElementMeasurement]:
        for item in measurements:
            for name, maximum in PLAUSIBLE_MAXIMUMS[item.element_type].items():
                value = getattr(item, name)
                if value is not None and value > maximum:
                    report.warnings.append(
                        f"Check the {item.element_type.value} on floor {item.floor_number}: "
                        f"its {_LABELS[name]} of {value:g} m is unusual (more than {maximum:g} m)"
                    )
        return measurements
