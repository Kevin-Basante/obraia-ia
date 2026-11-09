"""Summary writer for local development and tests: builds the text from the figures, without a model."""

from app.reports.schemas import RawSummary, ReportFigures, SummaryRequest


def _number(value: float, decimals: int = 1) -> str:
    """Colombian format, like the rest of the report: 1234.5 -> 1.234,5"""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".").removesuffix(",0")


def _money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}$ {_number(abs(value), 0)}"


SPANISH_LEVELS = {"low": "bajo", "medium": "medio", "high": "alto", "critical": "crítico"}


class FakeSummaryWriter:
    """Always the same sentences with the numbers of the report, in English or Spanish."""

    model_name = "fake"

    def ready(self) -> bool:
        return True

    def write(self, request: SummaryRequest) -> RawSummary:
        figures = request.figures
        if request.language == "es":
            return self._spanish(figures)
        return self._english(figures)

    @staticmethod
    def _english(figures: ReportFigures) -> RawSummary:
        work = figures.work
        sentences = [
            f"{figures.project.name} is {_number(work.progress_pct)}% done, with "
            f"{work.completed_tasks} of {work.task_count} tasks completed.",
            f"The current phase is {work.current_phase}." if work.current_phase else "No phase is moving yet.",
        ]
        recommendations = []
        if work.late_tasks:
            sentences.append(f"{work.late_tasks} tasks are past their planned end.")
            recommendations.append("Plan the late tasks again with the site manager.")
        if figures.money and figures.money.approved_budget:
            sentences.append(
                f"{_money(figures.money.total_spent)} of {_money(figures.money.approved_budget)} is spent."
            )
            recommendations.append("Compare the expenses with the approved budget every week.")
        if figures.risk:
            sentences.append(f"The risk is {figures.risk.level}, with a score of {_number(figures.risk.score)}.")
        recommendations.append("Keep reporting the progress of each task.")
        return RawSummary(summary=" ".join(sentences), recommendations=recommendations)

    @staticmethod
    def _spanish(figures: ReportFigures) -> RawSummary:
        work = figures.work
        sentences = [
            f"La obra {figures.project.name} va en el {_number(work.progress_pct)}%, con "
            f"{work.completed_tasks} de {work.task_count} tareas terminadas.",
            f"La fase actual es {work.current_phase}." if work.current_phase else "Todavía no hay fases en curso.",
        ]
        recommendations = []
        if work.late_tasks:
            sentences.append(f"Hay {work.late_tasks} tareas que pasaron su fecha de fin planeada.")
            recommendations.append("Reprogramar las tareas atrasadas con el maestro de obra.")
        if figures.money and figures.money.approved_budget:
            sentences.append(
                f"Se han gastado {_money(figures.money.total_spent)} de "
                f"{_money(figures.money.approved_budget)} aprobados."
            )
            recommendations.append("Comparar los gastos con el presupuesto aprobado cada semana.")
        if figures.risk:
            level = SPANISH_LEVELS.get(figures.risk.level, figures.risk.level)
            sentences.append(f"El riesgo es {level}, con un puntaje de {_number(figures.risk.score)}.")
        recommendations.append("Seguir reportando el avance de cada tarea.")
        return RawSummary(summary=" ".join(sentences), recommendations=recommendations)
