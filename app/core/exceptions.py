import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.error_codes import ErrorCode

logger = logging.getLogger("app.errors")


class AppError(HTTPException):
    def __init__(
        self,
        *,
        status_code: int,
        code: ErrorCode,
        message: str,
        details: object | None = None,
    ) -> None:
        detail: dict[str, object] = {
            "code": str(code),
            "message": message,
        }
        if details is not None:
            detail["details"] = details
        super().__init__(status_code=status_code, detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = _get_request_id(request)
        parsed = _parse_http_exception(exc)
        body = {
            "detail": parsed["detail"],
            "error": {
                "code": parsed["code"],
                "message": parsed["message"],
                "request_id": request_id,
            },
        }
        if parsed["details"] is not None:
            body["error"]["details"] = parsed["details"]
        logger.warning(
            "HTTP exception",
            extra={
                "event": "http_exception",
                "request_id": request_id,
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "error_code": parsed["code"],
                "error_message": parsed["message"],
            },
        )
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = _get_request_id(request)
        details = exc.errors()
        body = {
            "detail": details,
            "error": {
                "code": str(ErrorCode.VALIDATION_ERROR),
                "message": "request validation failed",
                "request_id": request_id,
                "details": details,
            },
        }
        logger.warning(
            "Validation exception",
            extra={
                "event": "validation_exception",
                "request_id": request_id,
                "status_code": 422,
                "path": request.url.path,
                "method": request.method,
                "error_code": "validation_error",
            },
        )
        return JSONResponse(status_code=422, content=body)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _get_request_id(request)
        body = {
            "detail": "internal server error",
            "error": {
                "code": str(ErrorCode.INTERNAL_SERVER_ERROR),
                "message": "internal server error",
                "request_id": request_id,
            },
        }
        logger.exception(
            "Unhandled exception",
            extra={
                "event": "unhandled_exception",
                "request_id": request_id,
                "status_code": 500,
                "path": request.url.path,
                "method": request.method,
                "error_code": str(ErrorCode.INTERNAL_SERVER_ERROR),
            },
        )
        return JSONResponse(status_code=500, content=body)


def _extract_message(detail: object, fallback: str) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, dict) and isinstance(detail.get("message"), str):
        return detail["message"]
    return fallback


def _http_code(status_code: int) -> str:
    mapping = {
        400: str(ErrorCode.BAD_REQUEST),
        401: str(ErrorCode.UNAUTHORIZED),
        403: str(ErrorCode.FORBIDDEN),
    }
    return mapping.get(status_code, f"http_{status_code}")


def _parse_http_exception(exc: HTTPException) -> dict[str, object]:
    default_message = _extract_message(exc.detail, fallback="request failed")
    code = _http_code(exc.status_code)
    details: object | None = None

    if isinstance(exc.detail, dict):
        raw_code = exc.detail.get("code")
        if isinstance(raw_code, str) and raw_code:
            code = raw_code
        message = _extract_message(exc.detail.get("message"), fallback=default_message)
        detail = message
        details = exc.detail.get("details")
    else:
        message = default_message
        detail = exc.detail

    return {
        "code": code,
        "message": message,
        "detail": detail,
        "details": details,
    }


def _get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)
