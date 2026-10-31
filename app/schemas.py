"""Shapes of the data the service receives from the model and sends to the backend."""

from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Same error shape as the backend: { "error": { "code", "message" } }."""

    error: ErrorBody
