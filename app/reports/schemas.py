"""Figures of a report as the backend sends them, and the summary the service answers."""

from typing import Literal

from pydantic import BaseModel, Field

# The longest summary and the most recommendations a report shows.
MAX_SUMMARY_CHARS = 1200
MAX_RECOMMENDATIONS = 4


class ProjectFigures(BaseModel):
    name: str
    type: str | None = None
    city: str | None = None
    status: str | None = None
    built_area_m2: float | None = None
    floors: int | None = None
    planned_start: str | None = None
    planned_end: str | None = None


class PhaseFigures(BaseModel):
    name: str
    status: str
    progress_pct: float = 0
    late: bool = False
    planned_end: str | None = None


class TaskFigures(BaseModel):
    name: str
    phase: str | None = None
    status: str
    progress_pct: float = 0
    late: bool = False
    planned_end: str | None = None


class WorkFigures(BaseModel):
    progress_pct: float = 0
    phase_count: int = 0
    completed_phases: int = 0
    task_count: int = 0
    completed_tasks: int = 0
    late_tasks: int = 0
    current_phase: str | None = None
    phases: list[PhaseFigures] = []
    upcoming_tasks: list[TaskFigures] = []


class CategoryFigures(BaseModel):
    category: str
    amount: float
    count: int = 0


class MoneyFigures(BaseModel):
    approved_budget: float | None = None
    total_spent: float = 0
    remaining: float | None = None
    spent_pct: float | None = None
    budget_versions: int = 0
    expense_count: int = 0
    by_category: list[CategoryFigures] = []


class FactorFigures(BaseModel):
    code: str
    score: float
    weight: float | None = None
    detail: str | None = None


class RiskFigures(BaseModel):
    level: str
    score: float
    predicted_delay_days: int = 0
    factors: list[FactorFigures] = []


class ReportFigures(BaseModel):
    """What the report shows. The public report has no money and no risk."""

    today: str | None = None
    project: ProjectFigures
    work: WorkFigures
    money: MoneyFigures | None = None
    risk: RiskFigures | None = None


class SummaryRequest(BaseModel):
    """Body of POST /api/v1/reports/summary."""

    language: Literal["en", "es"] = "en"
    report_type: Literal["public", "full"] = "public"
    figures: ReportFigures


class RawSummary(BaseModel):
    """What the model writes, before it is cleaned."""

    summary: str
    recommendations: list[str] = []


class SummaryResponse(BaseModel):
    """Answer of POST /api/v1/reports/summary."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "La obra va en el 36 % con la cimentación en curso y 7 tareas atrasadas.",
                    "recommendations": ["Reprogramar las tareas de la cimentación con el maestro de obra."],
                    "model": "gemini-3.5-flash",
                }
            ]
        }
    }

    summary: str = Field(description="A short paragraph about the state of the work")
    recommendations: list[str] = Field(description=f"Up to {MAX_RECOMMENDATIONS} concrete next steps")
    model: str


def clean_summary(raw: RawSummary) -> RawSummary:
    """Trims the text, drops empty lines and keeps the summary short."""
    summary = " ".join(raw.summary.split())
    if len(summary) > MAX_SUMMARY_CHARS:
        summary = summary[: MAX_SUMMARY_CHARS - 1].rsplit(" ", 1)[0] + "…"
    recommendations = [" ".join(line.split()) for line in raw.recommendations]
    recommendations = [line for line in recommendations if line][:MAX_RECOMMENDATIONS]
    return RawSummary(summary=summary, recommendations=recommendations)
