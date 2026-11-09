"""Figures of a report like the ones the backend sends."""

PUBLIC_FIGURES = {
    "today": "2026-11-09",
    "project": {
        "name": "Casa Basante",
        "type": "Vivienda unifamiliar",
        "city": "Pasto",
        "status": "in_progress",
        "built_area_m2": 96,
        "floors": 2,
        "planned_start": None,
        "planned_end": None,
    },
    "work": {
        "progress_pct": 36.4,
        "phase_count": 8,
        "completed_phases": 2,
        "task_count": 22,
        "completed_tasks": 5,
        "late_tasks": 7,
        "current_phase": "Cimentación",
        "phases": [
            {
                "name": "Cimentación",
                "status": "in_progress",
                "progress_pct": 70,
                "late": True,
                "planned_end": "2026-09-30",
            }
        ],
        "upcoming_tasks": [
            {
                "name": "Columnas",
                "phase": "Estructura",
                "status": "in_progress",
                "progress_pct": 20,
                "late": True,
                "planned_end": "2026-11-04",
            }
        ],
    },
}

FULL_FIGURES = {
    **PUBLIC_FIGURES,
    "money": {
        "approved_budget": 68645101,
        "total_spent": 270300000,
        "remaining": -201654899,
        "spent_pct": 393.76,
        "budget_versions": 3,
        "expense_count": 6,
        "by_category": [{"category": "materials", "amount": 261050000, "count": 3}],
    },
    "risk": {
        "level": "critical",
        "score": 89.5,
        "predicted_delay_days": 38,
        "factors": [{"code": "schedule_delay", "score": 100, "weight": 0.35, "detail": "7 tasks are late"}],
    },
}


def body(language="es", report_type="public", figures=None):
    return {"language": language, "report_type": report_type, "figures": figures or PUBLIC_FIGURES}
