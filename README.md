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

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn pytest httpx
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
```
