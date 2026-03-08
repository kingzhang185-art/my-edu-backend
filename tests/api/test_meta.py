from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_error_codes_endpoint_exposes_business_codes() -> None:
    response = client.get("/api/v1/meta/error-codes")

    assert response.status_code == 200
    body = response.json()
    assert body["TASK_NOT_FOUND"] == "task_not_found"
    assert body["PLAN_NOT_CONFIRMED"] == "plan_not_confirmed"
