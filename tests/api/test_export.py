from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _build_generated_course_id() -> str:
    created = client.post(
        "/api/v1/courses",
        json={"topic": "认识人民币", "subject": "数学", "grade": "一年级", "duration": 35},
    ).json()
    options = client.post(f"/api/v1/courses/{created['id']}/plan-options").json()
    client.post(
        f"/api/v1/courses/{created['id']}/confirm-plan",
        json={"option_id": options["items"][0]["id"]},
    )
    client.post(f"/api/v1/courses/{created['id']}/generate-lesson-plan")
    return created["id"]


def test_export_returns_download_url():
    generated_course_id = _build_generated_course_id()

    resp = client.post(
        f"/api/v1/courses/{generated_course_id}/export", json={"format": "pdf"}
    )
    assert resp.status_code == 202
    assert "export_id" in resp.json()
