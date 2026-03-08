import logging
import json
import re
from datetime import datetime, timezone


_BASE_RECORD = logging.LogRecord(
    name="base",
    level=logging.INFO,
    pathname=__file__,
    lineno=1,
    msg="base",
    args=(),
    exc_info=None,
)
_RESERVED_LOG_ATTRS = set(_BASE_RECORD.__dict__.keys())
_TOKEN_KEYWORDS = ("token", "authorization", "password", "secret", "api_key")
_EMAIL_KEYWORDS = ("email",)
_PHONE_KEYWORDS = ("phone", "mobile", "tel")
_EMAIL_PATTERN = re.compile(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b")
_PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")
_TOKEN_PATTERN = re.compile(
    r"(?i)\b(?:bearer\s+)?(?:token|access_token|refresh_token|api_key|authorization)\s*[:=]\s*[^\s,;]+"
)
_TOKEN_BEARER_PATTERN = re.compile(r"(?i)\bbearer\s+[a-z0-9\-._~+/]+=*")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self._redact_string(record.getMessage()),
        }

        for key, value in record.__dict__.items():
            if key in _RESERVED_LOG_ATTRS or key.startswith("_"):
                continue
            payload[key] = self._sanitize_value(key, value)

        if record.exc_info is not None:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _to_json_safe_value(value: object) -> object:
        try:
            json.dumps(value, ensure_ascii=False)
            return value
        except TypeError:
            return str(value)

    def _sanitize_value(self, key: str, value: object) -> object:
        key_lower = key.lower()
        if any(token in key_lower for token in _TOKEN_KEYWORDS):
            return "[REDACTED_TOKEN]"
        if any(email in key_lower for email in _EMAIL_KEYWORDS):
            return "[REDACTED_EMAIL]"
        if any(phone in key_lower for phone in _PHONE_KEYWORDS):
            return "[REDACTED_PHONE]"

        if isinstance(value, dict):
            return {k: self._sanitize_value(k, v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._sanitize_value(key, item) for item in value]
        if isinstance(value, tuple):
            return [self._sanitize_value(key, item) for item in value]
        if isinstance(value, str):
            return self._redact_string(value)

        json_safe = self._to_json_safe_value(value)
        if isinstance(json_safe, str):
            return self._redact_string(json_safe)
        return json_safe

    def _redact_string(self, value: str) -> str:
        value = _EMAIL_PATTERN.sub("[REDACTED_EMAIL]", value)
        value = _PHONE_PATTERN.sub("[REDACTED_PHONE]", value)
        value = _TOKEN_PATTERN.sub("[REDACTED_TOKEN]", value)
        value = _TOKEN_BEARER_PATTERN.sub("Bearer [REDACTED_TOKEN]", value)
        return value


def setup_logging(level: str) -> None:
    normalized_level = level.upper()
    resolved_level = getattr(logging, normalized_level, logging.INFO)
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(resolved_level)
