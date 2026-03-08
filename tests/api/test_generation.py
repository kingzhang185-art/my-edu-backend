from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _build_confirmed_course_id() -> str:
    created = client.post(
        "/api/v1/courses",
        json={"topic": "认识人民币", "subject": "数学", "grade": "一年级", "duration": 35},
    ).json()
    options = client.post(f"/api/v1/courses/{created['id']}/plan-options").json()
    client.post(
        f"/api/v1/courses/{created['id']}/confirm-plan",
        json={"option_id": options["items"][0]["id"]},
    )
    return created["id"]


def test_start_generation_returns_task_id():
    confirmed_course_id = _build_confirmed_course_id()

    resp = client.post(f"/api/v1/courses/{confirmed_course_id}/generate-lesson-plan")
    assert resp.status_code == 202
    assert "task_id" in resp.json()


def test_get_task_status():
    confirmed_course_id = _build_confirmed_course_id()

    started = client.post(f"/api/v1/courses/{confirmed_course_id}/generate-lesson-plan").json()
    task = client.get(f"/api/v1/tasks/{started['task_id']}")
    assert task.status_code == 200
    assert task.json()["status"] in {"pending", "running", "success", "failed"}
