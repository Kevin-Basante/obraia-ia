"""Entry point: uvicorn app.main:app"""

from fastapi import FastAPI

app = FastAPI(
    title="ObraIA AI service",
    description="Reads construction blueprints with a vision model and returns the measurements of each element.",
    version="0.1.0",
    docs_url="/docs",
)
