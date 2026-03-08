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

    refreshed = client.get(f"/api/v1/courses/{course_id}").json()
    assert refreshed["stage"] == "clarifying"


def test_list_messages_returns_history():
    created = client.post(
        "/api/v1/courses",
        json={"topic": "小学英语", "subject": "英语", "grade": "三年级", "duration": 40},
    )
    course_id = created.json()["id"]

    client.post(
        f"/api/v1/courses/{course_id}/chat",
        json={"message": "我要做一节小学英语课"},
    )

    resp = client.get(f"/api/v1/courses/{course_id}/messages")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) >= 2
    assert body["items"][0]["role"] == "user"
    assert body["items"][0]["content"] == "我要做一节小学英语课"
    assert body["items"][1]["role"] == "assistant"
