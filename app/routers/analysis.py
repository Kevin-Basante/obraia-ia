"""Reads a blueprint and returns its measurements."""

import logging
import time

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.analyzers.base import AnalyzerBusyError, AnalyzerError, BlueprintAnalyzer
from app.analyzers.factory import get_analyzer
from app.cleaning import clean_measurements
from app.config import Settings, get_settings
from app.errors import ServiceError
from app.file_types import detect_mime_type
from app.schemas import AnalysisResponse, ErrorResponse
from app.security import require_service_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/blueprints", tags=["Blueprints"], dependencies=[Depends(require_service_token)])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "The file is empty or not a PDF or image"},
        401: {"model": ErrorResponse, "description": "Missing or wrong X-Service-Token"},
        413: {"model": ErrorResponse, "description": "The file is too large"},
        502: {"model": ErrorResponse, "description": "The model failed or its answer was not valid"},
        503: {"model": ErrorResponse, "description": "The analyzer is not configured, or the model is busy"},
    },
)
async def analyze_blueprint(
    file: UploadFile = File(description="Blueprint as PDF, PNG, JPG or WEBP"),
    floors: int = Form(default=1, ge=1, le=2, description="Floors of the project"),
    settings: Settings = Depends(get_settings),
    analyzer: BlueprintAnalyzer = Depends(get_analyzer),
) -> AnalysisResponse:
    """Measurements of the elements drawn in the blueprint, ready to save in the backend."""
    content = await file.read()
    if not content:
        raise ServiceError(400, "EMPTY_FILE", "The file is empty")
    if len(content) > settings.max_file_bytes:
        raise ServiceError(413, "FILE_TOO_LARGE", f"The file is larger than {settings.max_file_mb} MB")
    mime_type = detect_mime_type(content)
    if mime_type is None:
        raise ServiceError(400, "UNSUPPORTED_FILE", "Only PDF, PNG, JPG and WEBP files can be analyzed")
    if not analyzer.ready():
        raise ServiceError(503, "ANALYZER_NOT_READY", "The analyzer has no API key")

    started = time.monotonic()
    try:
        # The SDK call blocks, so it runs outside the event loop.
        raw = await run_in_threadpool(analyzer.analyze, content, mime_type, floors)
    except AnalyzerBusyError as ex:
        logger.warning("Analysis of %s refused, the model is busy: %s", file.filename, ex)
        raise ServiceError(503, "ANALYZER_BUSY", str(ex)) from ex
    except AnalyzerError as ex:
        logger.error("Analysis of %s failed: %s", file.filename, ex)
        raise ServiceError(502, "ANALYZER_FAILED", str(ex)) from ex
    measurements, discarded = clean_measurements(raw.measurements, floors)
    return AnalysisResponse(
        measurements=measurements,
        warnings=raw.warnings,
        discarded=discarded,
        model=analyzer.model_name,
        elapsed_ms=int((time.monotonic() - started) * 1000),
    )
