"""Request ID: one short code per request, to find all its log lines together."""

import re
import uuid
from contextvars import ContextVar

HEADER = "X-Request-ID"
# Accepted from the caller only when it looks like an ID, so the logs stay clean.
_VALID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

_current: ContextVar[str] = ContextVar("request_id", default="-")


def new_request_id() -> str:
    return uuid.uuid4().hex


def pick_request_id(incoming: str | None) -> str:
    """The ID the caller sent when it is valid, or a new one."""
    if incoming and _VALID.match(incoming):
        return incoming
    return new_request_id()


def current_request_id() -> str:
    """ID of the request being handled, or "-" outside a request."""
    return _current.get()


def set_request_id(value: str):
    return _current.set(value)


def reset_request_id(token) -> None:
    _current.reset(token)
