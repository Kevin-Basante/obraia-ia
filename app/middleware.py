"""Middleware that runs around every request."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.request_id import HEADER, pick_request_id, reset_request_id, set_request_id

access_logger = logging.getLogger("app.access")

# Render calls /health often; logging it would hide the real requests.
QUIET_PATHS = frozenset({"/health"})


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Gives each request an ID and returns it in the X-Request-ID header."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = pick_request_id(request.headers.get(HEADER))
        token = set_request_id(request_id)
        started = time.monotonic()
        try:
            response = await call_next(request)
            if request.url.path not in QUIET_PATHS:
                elapsed_ms = int((time.monotonic() - started) * 1000)
                access_logger.info(
                    "%s %s -> %d in %d ms", request.method, request.url.path, response.status_code, elapsed_ms
                )
        finally:
            reset_request_id(token)
        response.headers[HEADER] = request_id
        return response
