"""Errors of the service and how they are answered: { "error": { "code", "message" } }."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ServiceError)
    async def service_error(_: Request, ex: ServiceError) -> JSONResponse:
        return JSONResponse(status_code=ex.status, content=error_body(ex.code, ex.message))

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, ex: RequestValidationError) -> JSONResponse:
        fields = ", ".join(".".join(str(part) for part in error["loc"][1:]) for error in ex.errors())
        return JSONResponse(status_code=400, content=error_body("VALIDATION_ERROR", f"Invalid fields: {fields}"))

    @app.exception_handler(HTTPException)
    async def http_error(_: Request, ex: HTTPException) -> JSONResponse:
        codes = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
        code = codes.get(ex.status_code, "HTTP_ERROR")
        return JSONResponse(status_code=ex.status_code, content=error_body(code, str(ex.detail)), headers=ex.headers)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, ex: Exception) -> JSONResponse:
        # The details stay in the log; the caller only learns that something failed.
        logger.exception("Unexpected error in %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content=error_body("INTERNAL_ERROR", "Unexpected error in the AI service"))
