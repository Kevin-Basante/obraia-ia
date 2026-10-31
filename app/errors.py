"""Errors of the service and how they are answered: { "error": { "code", "message" } }."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


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
