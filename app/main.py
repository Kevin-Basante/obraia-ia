"""Entry point: uvicorn app.main:app"""

from fastapi import FastAPI

from app import __version__
from app.errors import register_error_handlers
from app.logging_setup import configure_logging
from app.middleware import RequestIdMiddleware
from app.routers import analysis, elements, health, reports

# Messages of the service (retries, failures) appear in the Render logs.
configure_logging()

TAGS = [
    {"name": "Health", "description": "State of the service, for Render and the backend"},
    {"name": "Blueprints", "description": "Reads a blueprint and returns its measurements"},
    {"name": "Elements", "description": "Element types the service measures"},
    {"name": "Reports", "description": "Writes the summary of a PDF report from its figures"},
]

app = FastAPI(
    title="ObraIA AI service",
    description=(
        "Reads construction blueprints with a vision model and returns the measurements of each element. "
        "It also writes the summary of the PDF reports of the backend."
    ),
    version=__version__,
    docs_url="/docs",
    openapi_tags=TAGS,
)
register_error_handlers(app)
app.add_middleware(RequestIdMiddleware)
app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(elements.router)
app.include_router(reports.router)
