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


def test_list_courses_returns_latest_first():
    older = client.post(
        "/api/v1/courses",
        json={"topic": "旧课程", "subject": "英语", "grade": "三年级", "duration": 35},
    ).json()
    newer = client.post(
        "/api/v1/courses",
        json={"topic": "新课程", "subject": "数学", "grade": "四年级", "duration": 40},
    ).json()

    resp = client.get("/api/v1/courses")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert body[0]["id"] == newer["id"]
    assert body[1]["id"] == older["id"]
    assert body[0]["topic"] == "新课程"


def test_update_course_topic():
    created = client.post(
        "/api/v1/courses",
        json={"topic": "待更新课程", "subject": "语文", "grade": "五年级", "duration": 40},
    ).json()

    updated = client.patch(
        f"/api/v1/courses/{created['id']}",
        json={"topic": "已更新课程"},
    )
    assert updated.status_code == 200
    assert updated.json()["topic"] == "已更新课程"

    fetched = client.get(f"/api/v1/courses/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["topic"] == "已更新课程"
