"""Middleware that runs around every request."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.request_id import HEADER, pick_request_id, reset_request_id, set_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Gives each request an ID and returns it in the X-Request-ID header."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = pick_request_id(request.headers.get(HEADER))
        token = set_request_id(request_id)
        try:
            response = await call_next(request)
        finally:
            reset_request_id(token)
        response.headers[HEADER] = request_id
        return response
