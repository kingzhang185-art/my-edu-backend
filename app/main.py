from fastapi import FastAPI

from app.api.v1.chat import router as chat_router
from app.api.v1.courses import router as courses_router
from app.api.v1.tasks import router as tasks_router

app = FastAPI()
app.include_router(courses_router)
app.include_router(chat_router)
app.include_router(tasks_router)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
