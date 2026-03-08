from fastapi.testclient import TestClient

from app.db.models import (
    CoursePlanOptionModel,
    CourseProjectVersionModel,
    ExportRecordModel,
    GenerationTaskItemModel,
    GenerationTaskModel,
    UsageLogModel,
)
from app.db.session import SessionLocal
from app.main import app


client = TestClient(app)


def test_core_tables_are_written_by_main_flow():
    created = client.post(
        "/api/v1/courses",
        json={"topic": "分数加减法", "subject": "数学", "grade": "四年级", "duration": 40},
    ).json()
    course_id = created["id"]

    options = client.post(f"/api/v1/courses/{course_id}/plan-options").json()
    client.post(
        f"/api/v1/courses/{course_id}/confirm-plan",
        json={"option_id": options["items"][0]["id"]},
    )
    task = client.post(f"/api/v1/courses/{course_id}/generate-lesson-plan").json()
    client.post(f"/api/v1/courses/{course_id}/export", json={"format": "pdf"})

    with SessionLocal() as session:
        assert (
            session.query(CoursePlanOptionModel)
            .filter(CoursePlanOptionModel.course_id == int(course_id))
            .count()
            == 3
        )
        assert session.query(CourseProjectVersionModel).count() >= 1
        assert session.query(GenerationTaskModel).filter(GenerationTaskModel.id == task["task_id"]).count() == 1
        assert (
            session.query(GenerationTaskItemModel)
            .filter(GenerationTaskItemModel.task_id == task["task_id"])
            .count()
            == 2
        )
        persisted_task = session.query(GenerationTaskModel).filter(GenerationTaskModel.id == task["task_id"]).one()
        assert persisted_task.status == "success"
        item_keys = {
            row.item_key
            for row in session.query(GenerationTaskItemModel)
            .filter(GenerationTaskItemModel.task_id == task["task_id"])
            .all()
        }
        assert item_keys == {"lesson_plan", "quality_check"}
        assert (
            session.query(ExportRecordModel)
            .filter(ExportRecordModel.course_id == int(course_id))
            .count()
            == 1
        )
        assert (
            session.query(UsageLogModel)
            .filter(UsageLogModel.course_id == int(course_id))
            .count()
            >= 4
        )
