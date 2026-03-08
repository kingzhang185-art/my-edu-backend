# Backend Local Development Runbook

## 1. Start Infrastructure

```bash
docker compose up -d mysql redis mongo
```

Recommended local ports:
- MySQL: `3306`
- Redis: `6379`
- MongoDB: `27017`

## 2. Configure Environment

Copy `.env.example` to `.env` and adjust values as needed.

## 3. Start API Service

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 4. Run Verification

```bash
python -m pytest -q
curl -s http://localhost:8000/api/v1/health
```

Expected health response:

```json
{"status":"ok"}
```
