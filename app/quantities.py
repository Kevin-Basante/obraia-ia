"""Amount of work each measurement represents: m3 of concrete or m2 of surface."""

from app.elements import ElementType
from app.schemas import ElementMeasurement

VOLUME_ELEMENTS = frozenset({ElementType.FOUNDATION, ElementType.COLUMN, ElementType.BEAM, ElementType.SLAB})


def unit_of(element: ElementType) -> str:
    return "m3" if element in VOLUME_ELEMENTS else "m2"


def quantity_of(item: ElementMeasurement) -> float:
    """Volume for concrete elements, wall area (length by height) or surface (length by width), times quantity."""
    if item.element_type in VOLUME_ELEMENTS:
        size = item.length_m * item.width_m * item.height_m
    elif item.element_type == ElementType.WALL:
        size = item.length_m * item.height_m
    else:
        size = item.length_m * item.width_m
    return round(size * item.quantity, 2)
