"""Health check, used by Render and by the backend before analyzing."""

from fastapi import APIRouter, Depends

from app.analyzers.base import BlueprintAnalyzer
from app.analyzers.factory import get_analyzer
from app.config import Settings, get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(get_settings),
    analyzer: BlueprintAnalyzer = Depends(get_analyzer),
) -> HealthResponse:
    """The service is up; ready says whether it can analyze (the API key is set)."""
    return HealthResponse(status="UP", analyzer=settings.analyzer, model=analyzer.model_name, ready=analyzer.ready())
