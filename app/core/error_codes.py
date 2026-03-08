import json
from enum import StrEnum
from pathlib import Path


DEFAULT_ERROR_CODES: dict[str, str] = {
    "BAD_REQUEST": "bad_request",
    "UNAUTHORIZED": "unauthorized",
    "FORBIDDEN": "forbidden",
    "VALIDATION_ERROR": "validation_error",
    "INTERNAL_SERVER_ERROR": "internal_server_error",
    "COURSE_NOT_FOUND": "course_not_found",
    "TASK_NOT_FOUND": "task_not_found",
    "TASK_ITEM_NOT_FOUND": "task_item_not_found",
    "DELIVERABLE_NOT_FOUND": "deliverable_not_found",
    "PLAN_NOT_CONFIRMED": "plan_not_confirmed",
    "UNSUPPORTED_EXPORT_FORMAT": "unsupported_export_format",
}


def _load_shared_codes() -> dict[str, str]:
    repo_local_path = Path(__file__).with_name("error_codes.json")
    workspace_shared_path = Path(__file__).resolve().parents[3] / "shared" / "error_codes.json"

    for codes_path in (repo_local_path, workspace_shared_path):
        if codes_path.exists():
            return json.loads(codes_path.read_text(encoding="utf-8"))

    return dict(DEFAULT_ERROR_CODES)


SHARED_ERROR_CODES = _load_shared_codes()


class ErrorCode(StrEnum):
    BAD_REQUEST = SHARED_ERROR_CODES["BAD_REQUEST"]
    UNAUTHORIZED = SHARED_ERROR_CODES["UNAUTHORIZED"]
    FORBIDDEN = SHARED_ERROR_CODES["FORBIDDEN"]
    VALIDATION_ERROR = SHARED_ERROR_CODES["VALIDATION_ERROR"]
    INTERNAL_SERVER_ERROR = SHARED_ERROR_CODES["INTERNAL_SERVER_ERROR"]
    COURSE_NOT_FOUND = SHARED_ERROR_CODES["COURSE_NOT_FOUND"]
    TASK_NOT_FOUND = SHARED_ERROR_CODES["TASK_NOT_FOUND"]
    TASK_ITEM_NOT_FOUND = SHARED_ERROR_CODES["TASK_ITEM_NOT_FOUND"]
    DELIVERABLE_NOT_FOUND = SHARED_ERROR_CODES["DELIVERABLE_NOT_FOUND"]
    PLAN_NOT_CONFIRMED = SHARED_ERROR_CODES["PLAN_NOT_CONFIRMED"]
    UNSUPPORTED_EXPORT_FORMAT = SHARED_ERROR_CODES["UNSUPPORTED_EXPORT_FORMAT"]


def list_error_codes() -> dict[str, str]:
    return dict(SHARED_ERROR_CODES)
