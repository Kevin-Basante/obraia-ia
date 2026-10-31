"""Entry point: uvicorn app.main:app"""

import logging

from fastapi import FastAPI

from app.errors import register_error_handlers
from app.routers import analysis, health

# Messages of the service (retries, failures) appear in the Render logs.
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(
    title="ObraIA AI service",
    description="Reads construction blueprints with a vision model and returns the measurements of each element.",
    version="0.1.0",
    docs_url="/docs",
)
register_error_handlers(app)
app.include_router(health.router)
app.include_router(analysis.router)
