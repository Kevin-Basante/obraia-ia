"""Analyzer for local development and tests: answers without calling any model."""

from app.schemas import RawAnalysis, RawMeasurement


class FakeAnalyzer:
    """Returns the same small house every time: walls, a slab and a roof."""

    model_name = "fake"

    def ready(self) -> bool:
        return True

    def analyze(self, content: bytes, mime_type: str, floors: int) -> RawAnalysis:
        measurements = [
            RawMeasurement(element_type="wall", floor_number=1, length_m=36.0, height_m=2.4, notes="Muros de fachada"),
            RawMeasurement(element_type="foundation", floor_number=1, length_m=36.0, width_m=0.4, height_m=0.5),
            RawMeasurement(element_type="slab", floor_number=1, length_m=9.0, width_m=8.0, height_m=0.12),
            RawMeasurement(element_type="roof", floor_number=floors, length_m=9.0, width_m=8.0),
        ]
        return RawAnalysis(measurements=measurements, warnings=["Medidas de ejemplo: el servicio corre sin IA"])
