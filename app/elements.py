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
