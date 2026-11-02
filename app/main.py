"""Entry point: uvicorn app.main:app"""

from fastapi import FastAPI

from app import __version__
from app.errors import register_error_handlers
from app.logging_setup import configure_logging
from app.middleware import RequestIdMiddleware
from app.routers import analysis, elements, health

# Messages of the service (retries, failures) appear in the Render logs.
configure_logging()

app = FastAPI(
    title="ObraIA AI service",
    description="Reads construction blueprints with a vision model and returns the measurements of each element.",
    version=__version__,
    docs_url="/docs",
)
register_error_handlers(app)
app.add_middleware(RequestIdMiddleware)
app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(elements.router)
