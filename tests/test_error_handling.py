from fastapi.testclient import TestClient

from app.main import app


def test_http_exception_uses_standard_error_payload() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/tasks/not-exists")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "task not found"
    assert body["error"]["code"] == "task_not_found"
    assert body["error"]["message"] == "task not found"
    assert body["error"]["request_id"] == response.headers["x-request-id"]


def test_validation_error_uses_standard_error_payload() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/courses", json={"topic": "only-topic"})

    assert response.status_code == 422
    body = response.json()
    assert isinstance(body["detail"], list)
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "request validation failed"
    assert isinstance(body["error"]["details"], list)
    assert body["error"]["request_id"] == response.headers["x-request-id"]


def test_business_error_code_for_plan_not_confirmed() -> None:
    client = TestClient(app)
    created = client.post(
        "/api/v1/courses",
        json={"topic": "小学英语", "subject": "英语", "grade": "三年级", "duration": 40},
    )
    course_id = created.json()["id"]

    response = client.post(f"/api/v1/courses/{course_id}/generate-lesson-plan")

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "plan_not_confirmed"
    assert body["error"]["message"] == "plan not confirmed"
