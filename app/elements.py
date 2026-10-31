"""Building elements the service measures. They match the element types of the backend."""

from enum import Enum


class ElementType(str, Enum):
    FOUNDATION = "foundation"
    COLUMN = "column"
    BEAM = "beam"
    SLAB = "slab"
    WALL = "wall"
    FLOOR = "floor"
    ROOF = "roof"


# Dimensions each element needs, in meters. Concrete elements are volumes
# (m3); walls are length by height, floors and roofs length by width (m2).
REQUIRED_DIMENSIONS: dict[ElementType, tuple[str, ...]] = {
    ElementType.FOUNDATION: ("length_m", "width_m", "height_m"),
    ElementType.COLUMN: ("length_m", "width_m", "height_m"),
    ElementType.BEAM: ("length_m", "width_m", "height_m"),
    ElementType.SLAB: ("length_m", "width_m", "height_m"),
    ElementType.WALL: ("length_m", "height_m"),
    ElementType.FLOOR: ("length_m", "width_m"),
    ElementType.ROOF: ("length_m", "width_m"),
}

ALL_DIMENSIONS = ("length_m", "width_m", "height_m")
