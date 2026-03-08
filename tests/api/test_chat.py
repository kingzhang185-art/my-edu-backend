from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_returns_clarification_question():
    created = client.post(
        "/api/v1/courses",
        json={"topic": "小学英语", "subject": "英语", "grade": "三年级", "duration": 40},
    )
    course_id = created.json()["id"]

    resp = client.post(
        f"/api/v1/courses/{course_id}/chat",
        json={"message": "我要做一节小学英语课"},
    )

    assert resp.status_code == 200
    assert "next_question" in resp.json()
