"""Only the ObraIA backend may call the service: it sends the shared token in X-Service-Token."""

import secrets

from fastapi import Depends, Header

from app.config import Settings, get_settings
from app.errors import ServiceError


def require_service_token(
    x_service_token: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if not settings.service_token:
        raise ServiceError(503, "SERVICE_NOT_CONFIGURED", "SERVICE_TOKEN is not set on the server")
    if not x_service_token or not secrets.compare_digest(x_service_token, settings.service_token):
        raise ServiceError(401, "INVALID_SERVICE_TOKEN", "Missing or wrong X-Service-Token header")
