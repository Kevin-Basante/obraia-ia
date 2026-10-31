"""Turns the free answer of the model into measurements the backend accepts."""

from app.elements import ElementType

_ALIASES = {
    "foundations": ElementType.FOUNDATION,
    "footing": ElementType.FOUNDATION,
    "columns": ElementType.COLUMN,
    "beams": ElementType.BEAM,
    "slabs": ElementType.SLAB,
    "walls": ElementType.WALL,
    "floors": ElementType.FLOOR,
    "roofs": ElementType.ROOF,
}


def parse_element(value: str) -> ElementType | None:
    """"Walls", " wall " and "WALL" all become ElementType.WALL; unknown names give None."""
    key = value.strip().lower()
    try:
        return ElementType(key)
    except ValueError:
        return _ALIASES.get(key)
