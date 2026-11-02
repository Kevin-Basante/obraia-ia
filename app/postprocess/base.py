"""Chain of steps (Chain of Responsibility): each step does its part and hands the list to the next."""

from dataclasses import dataclass, field
from typing import Protocol

from app.schemas import ElementMeasurement


@dataclass
class Report:
    """What the steps tell the user: notes for the warnings list and how many rows were merged."""

    warnings: list[str] = field(default_factory=list)
    merged: int = 0


class PostprocessStep(Protocol):
    def apply(self, measurements: list[ElementMeasurement], report: Report) -> list[ElementMeasurement]: ...


class Pipeline:
    """Runs the steps in order; adding a step does not change the others or the route."""

    def __init__(self, steps: list[PostprocessStep]):
        self.steps = steps

    def run(self, measurements: list[ElementMeasurement]) -> tuple[list[ElementMeasurement], Report]:
        report = Report()
        for step in self.steps:
            measurements = step.apply(measurements, report)
        return measurements, report
