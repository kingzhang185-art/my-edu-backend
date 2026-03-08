from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_course():
    payload = {
        "topic": "过去进行时",
        "subject": "英语",
        "grade": "八年级",
        "duration": 45,
    }
    resp = client.post("/api/v1/courses", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["topic"] == "过去进行时"
    assert body["stage"] == "draft"


def test_get_course():
    payload = {
        "topic": "过去进行时",
        "subject": "英语",
        "grade": "八年级",
        "duration": 45,
    }
    created = client.post("/api/v1/courses", json=payload).json()

    resp = client.get(f"/api/v1/courses/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]
