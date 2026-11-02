import logging

from app.logging_setup import LOG_FORMAT, RequestIdFilter, configure_logging
from app.request_id import reset_request_id, set_request_id


def record() -> logging.LogRecord:
    return logging.LogRecord("app.test", logging.INFO, __file__, 1, "hello", None, None)


def test_filter_adds_the_current_request_id():
    token = set_request_id("req-7")
    try:
        item = record()
        assert RequestIdFilter().filter(item) is True
        assert item.request_id == "req-7"
    finally:
        reset_request_id(token)


def test_filter_uses_a_dash_outside_requests():
    item = record()
    RequestIdFilter().filter(item)
    assert item.request_id == "-"


def test_format_shows_level_request_and_message():
    item = record()
    RequestIdFilter().filter(item)
    assert logging.Formatter(LOG_FORMAT).format(item) == "INFO [-] app.test: hello"


def test_configure_logging_sets_one_handler_with_the_filter():
    configure_logging(logging.WARNING)
    root = logging.getLogger()
    assert len(root.handlers) == 1
    assert root.level == logging.WARNING
    assert any(isinstance(item, RequestIdFilter) for item in root.handlers[0].filters)
    configure_logging()
