import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.api.v1.chat import router as chat_router
from app.api.v1.courses import router as courses_router
from app.api.v1.deliverables import router as deliverables_router
from app.api.v1.export import router as export_router
from app.api.v1.tasks import router as tasks_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.init_db import init_db

logger = logging.getLogger("app.http")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.log_level)
    init_db()
    logging.getLogger("app.lifecycle").info("Application startup completed")
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
app.include_router(courses_router)
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(deliverables_router)
app.include_router(export_router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get("x-request-id") or str(uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "%s %s -> %s (%sms) request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
