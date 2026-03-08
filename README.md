# My EDU Backend

FastAPI backend for the AI lesson-plan MVP.

## Prerequisites

- Python 3.11+
- Docker + Docker Compose (for MySQL, Redis, MongoDB)

## Start Local Infra

```bash
cp .env.example .env
docker compose up -d mysql redis mongo
```

Key runtime env vars:
- `LOG_LEVEL` (default: `INFO`)
- `CORS_ALLOW_ORIGINS` (comma-separated origins)

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Database Migration

```bash
source .venv/bin/activate
alembic upgrade head
```

## Run

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
source .venv/bin/activate
python -m pytest -q
```

## API Smoke

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/meta/error-codes
```

Error response shape (unified):

```json
{
  "detail": "task not found",
  "error": {
    "code": "task_not_found",
    "message": "task not found",
    "request_id": "..."
  }
}
```
