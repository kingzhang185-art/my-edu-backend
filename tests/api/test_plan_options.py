from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_generate_and_confirm_plan():
    created = client.post(
        "/api/v1/courses",
        json={"topic": "分数加减法", "subject": "数学", "grade": "四年级", "duration": 40},
    ).json()

    options = client.post(f"/api/v1/courses/{created['id']}/plan-options").json()
    assert len(options["items"]) == 3
    course_after_options = client.get(f"/api/v1/courses/{created['id']}").json()
    assert course_after_options["stage"] == "options_ready"

    confirm = client.post(
        f"/api/v1/courses/{created['id']}/confirm-plan",
        json={"option_id": options["items"][0]["id"]},
    )
    assert confirm.status_code == 200
    assert confirm.json()["stage"] == "plan_confirmed"
