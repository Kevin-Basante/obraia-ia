"""Writes the summary of a PDF report of the backend."""

import logging

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.analyzers.base import AnalyzerBusyError, AnalyzerError
from app.errors import ServiceError
from app.limiter import AnalysisLimiter, get_limiter
from app.reports.base import SummaryWriter
from app.reports.factory import get_summary_writer
from app.reports.schemas import SummaryRequest, SummaryResponse, clean_summary
from app.schemas import ErrorResponse
from app.security import require_service_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"], dependencies=[Depends(require_service_token)])


@router.post(
    "/summary",
    response_model=SummaryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "The figures are missing or not valid"},
        401: {"model": ErrorResponse, "description": "Missing or wrong X-Service-Token"},
        502: {"model": ErrorResponse, "description": "The model failed or its answer was not valid"},
        503: {"model": ErrorResponse, "description": "The writer is not configured, or the model is busy"},
    },
)
async def write_summary(
    request: SummaryRequest,
    writer: SummaryWriter = Depends(get_summary_writer),
    limiter: AnalysisLimiter = Depends(get_limiter),
) -> SummaryResponse:
    """A short summary and a few recommendations, in the language of the report."""
    if not writer.ready():
        raise ServiceError(503, "ANALYZER_NOT_READY", "The summary writer has no API key")
    try:
        # It shares the slots of the analyses: the free plan of Render has little memory.
        with limiter.slot():
            raw = await run_in_threadpool(writer.write, request)
    except AnalyzerBusyError as ex:
        logger.warning("Summary of %s refused, the model is busy: %s", request.figures.project.name, ex)
        raise ServiceError(503, "ANALYZER_BUSY", str(ex)) from ex
    except AnalyzerError as ex:
        logger.error("Summary of %s failed: %s", request.figures.project.name, ex)
        raise ServiceError(502, "ANALYZER_FAILED", str(ex)) from ex
    cleaned = clean_summary(raw)
    if not cleaned.summary:
        raise ServiceError(502, "ANALYZER_FAILED", "The model answered an empty summary")
    return SummaryResponse(summary=cleaned.summary, recommendations=cleaned.recommendations, model=writer.model_name)
