"""Turns the free answer of the model into measurements the backend accepts."""

from pydantic import ValidationError

from app.elements import ALL_DIMENSIONS, REQUIRED_DIMENSIONS, ElementType
from app.schemas import ElementMeasurement, RawMeasurement

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


def clean_measurement(raw: RawMeasurement, floors: int) -> ElementMeasurement | None:
    """A valid measurement, or None when the element or its dimensions are not usable.

    Only the dimensions the element needs are kept, rounded to centimeters,
    and the floor must exist in the project.
    """
    element = parse_element(raw.element_type)
    if element is None:
        return None
    floor = raw.floor_number or 1
    if floor > floors:
        return None
    required = REQUIRED_DIMENSIONS[element]
    values: dict[str, float | None] = {}
    for name in ALL_DIMENSIONS:
        value = getattr(raw, name)
        if name not in required:
            values[name] = None
        elif value is None or value <= 0:
            return None
        else:
            values[name] = round(value, 2)
    try:
        return ElementMeasurement(
            element_type=element,
            floor_number=floor,
            quantity=raw.quantity or 1,
            notes=(raw.notes or "").strip()[:500] or None,
            **values,
        )
    except ValidationError:
        return None
