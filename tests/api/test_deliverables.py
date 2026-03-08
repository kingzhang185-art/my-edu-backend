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


def test_get_latest_deliverable():
    generated_course_id = _build_generated_course_id()

    resp = client.get(f"/api/v1/courses/{generated_course_id}/deliverables/latest")
    assert resp.status_code == 200
    assert "timeline" in resp.json()["lesson_plan"]


def test_regenerate_section():
    generated_course_id = _build_generated_course_id()

    resp = client.post(
        f"/api/v1/courses/{generated_course_id}/deliverables/timeline/regenerate"
    )
    assert resp.status_code == 200
    assert "lesson_plan" in resp.json()


def test_regenerate_exercises_preserves_expected_shape():
    generated_course_id = _build_generated_course_id()

    resp = client.post(
        f"/api/v1/courses/{generated_course_id}/deliverables/exercises/regenerate"
    )
    assert resp.status_code == 200
    assert isinstance(resp.json()["lesson_plan"]["exercises"], list)
