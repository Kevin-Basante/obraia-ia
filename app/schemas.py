"""Shapes of the data the service receives from the model and sends to the backend."""

from pydantic import BaseModel, Field

from app.elements import ElementType


class ElementMeasurement(BaseModel):
    """One measured element, like 4 walls of 3.5 m by 2.4 m on floor 1."""

    element_type: ElementType
    floor_number: int = Field(ge=1, le=2)
    length_m: float = Field(gt=0, le=1000)
    width_m: float | None = Field(default=None, gt=0, le=1000)
    height_m: float | None = Field(default=None, gt=0, le=1000)
    quantity: int = Field(default=1, ge=1, le=1000)
    notes: str | None = Field(default=None, max_length=500)


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Same error shape as the backend: { "error": { "code", "message" } }."""

    error: ErrorBody
