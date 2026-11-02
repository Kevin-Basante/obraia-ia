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


class RawMeasurement(BaseModel):
    """What the model returns for each element, before it is checked."""

    element_type: str
    floor_number: int | None = None
    length_m: float | None = None
    width_m: float | None = None
    height_m: float | None = None
    quantity: int | None = None
    notes: str | None = None


class RawAnalysis(BaseModel):
    """Full answer of the model: the elements and what it could not read."""

    measurements: list[RawMeasurement]
    warnings: list[str] = []


class ElementSummary(BaseModel):
    """Totals of one element type, to show the size of the work at a glance."""

    element_type: ElementType
    rows: int = Field(description="Measurement rows of this element")
    pieces: int = Field(description="Sum of the quantities")
    total: float = Field(description="Total volume or surface")
    unit: str = Field(description="m3 for concrete elements, m2 for walls, floors and roofs")


class AnalysisResponse(BaseModel):
    """Answer of POST /api/v1/blueprints/analyze."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "measurements": [
                        {
                            "element_type": "wall",
                            "floor_number": 1,
                            "length_m": 36.0,
                            "width_m": None,
                            "height_m": 2.4,
                            "quantity": 1,
                            "notes": "Muros de fachada",
                        }
                    ],
                    "warnings": ["Escala no visible"],
                    "discarded": 0,
                    "merged": 0,
                    "summary": [{"element_type": "wall", "rows": 1, "pieces": 1, "total": 86.4, "unit": "m2"}],
                    "model": "gemini-3.5-flash",
                    "elapsed_ms": 8400,
                }
            ]
        }
    }

    measurements: list[ElementMeasurement]
    warnings: list[str]
    discarded: int = Field(description="Elements the model returned that were not valid")
    merged: int = Field(default=0, description="Repeated rows joined into one")
    summary: list[ElementSummary] = Field(default=[], description="Totals per element type")
    model: str
    elapsed_ms: int


class ElementInfo(BaseModel):
    """An element the service can measure and the dimensions it needs."""

    element_type: ElementType
    required_dimensions: list[str]
    unit: str


class HealthResponse(BaseModel):
    """Answer of GET /health."""

    status: str = Field(description="Always UP when the service answers")
    analyzer: str = Field(description="gemini or fake")
    model: str = Field(description="Main model that reads the blueprints")
    ready: bool = Field(description="False when the analyzer is missing its API key")
    version: str = Field(description="Version of the service")
    uptime_seconds: int = Field(description="Seconds since the service started")


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Same error shape as the backend: { "error": { "code", "message" } }."""

    error: ErrorBody
