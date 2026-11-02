"""Puts the rows in the order a builder reads them: floor by floor, from the ground up."""

from app.elements import ElementType
from app.postprocess.base import Report
from app.schemas import ElementMeasurement

BUILD_ORDER = list(ElementType)


class SortByFloorAndElement:
    """Floor 1 first; inside a floor, foundation, columns, beams... as listed in ElementType."""

    def apply(self, measurements: list[ElementMeasurement], report: Report) -> list[ElementMeasurement]:
        return sorted(measurements, key=lambda item: (item.floor_number, BUILD_ORDER.index(item.element_type)))
