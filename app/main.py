from fastapi import FastAPI

from app.api.v1.courses import router as courses_router

app = FastAPI()
app.include_router(courses_router)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
