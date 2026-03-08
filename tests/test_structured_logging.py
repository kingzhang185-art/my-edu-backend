import json
import logging

from app.core.logging import JsonFormatter


def test_json_formatter_outputs_structured_log() -> None:
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=11,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    record.request_id = "req-123"
    record.method = "GET"
    record.path = "/api/v1/health"
    record.status_code = 200
    record.duration_ms = 3.14

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.test"
    assert payload["message"] == "hello world"
    assert payload["request_id"] == "req-123"
    assert payload["method"] == "GET"
    assert payload["path"] == "/api/v1/health"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] == 3.14


def test_json_formatter_redacts_email_phone_and_token() -> None:
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=33,
        msg="user email=alice@example.com phone=13812345678 token=abcDEF1234567890",
        args=(),
        exc_info=None,
    )
    record.access_token = "abcDEF1234567890"
    record.contact_email = "alice@example.com"
    record.mobile_phone = "13812345678"
    record.profile = {
        "email": "alice@example.com",
        "phone": "13812345678",
        "token": "abcDEF1234567890",
    }

    formatted = JsonFormatter().format(record)
    payload = json.loads(formatted)

    assert "alice@example.com" not in formatted
    assert "13812345678" not in formatted
    assert "abcDEF1234567890" not in formatted
    assert "[REDACTED_EMAIL]" in payload["message"]
    assert "[REDACTED_PHONE]" in payload["message"]
    assert "[REDACTED_TOKEN]" in payload["message"]
    assert payload["access_token"] == "[REDACTED_TOKEN]"
    assert payload["contact_email"] == "[REDACTED_EMAIL]"
    assert payload["mobile_phone"] == "[REDACTED_PHONE]"
    assert payload["profile"]["email"] == "[REDACTED_EMAIL]"
    assert payload["profile"]["phone"] == "[REDACTED_PHONE]"
    assert payload["profile"]["token"] == "[REDACTED_TOKEN]"
