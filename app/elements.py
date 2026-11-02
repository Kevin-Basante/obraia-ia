"""Building elements the service measures. They match the element types of the backend."""

from enum import StrEnum


class ElementType(StrEnum):
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

# Largest size that makes sense for each dimension in a house of up to 2 floors.
# A bigger value is kept, but the user is warned to check it on the blueprint.
PLAUSIBLE_MAXIMUMS: dict[ElementType, dict[str, float]] = {
    ElementType.FOUNDATION: {"length_m": 100, "width_m": 2, "height_m": 2},
    ElementType.COLUMN: {"length_m": 1.5, "width_m": 1.5, "height_m": 8},
    ElementType.BEAM: {"length_m": 15, "width_m": 1, "height_m": 1.5},
    ElementType.SLAB: {"length_m": 40, "width_m": 40, "height_m": 0.5},
    ElementType.WALL: {"length_m": 100, "height_m": 6},
    ElementType.FLOOR: {"length_m": 40, "width_m": 40},
    ElementType.ROOF: {"length_m": 40, "width_m": 40},
}
