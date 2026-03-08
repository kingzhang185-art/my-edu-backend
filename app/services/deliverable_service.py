import json

from fastapi import HTTPException

from app.db.models import CourseProjectVersionModel
from app.db.session import SessionLocal


class SqlDeliverableService:
    def upsert_placeholder(self, course_id: str) -> dict:
        lesson_plan = {
            "meta": {"course_id": course_id},
            "objectives": [],
            "timeline": [{"phase": "导入", "minutes": 5}],
            "teacher_script": [],
            "board_plan": "",
            "exercises": [],
        }
        return self._create_version(course_id, lesson_plan, source="generate")

    def get_latest(self, course_id: str) -> dict:
        parsed_id = _parse_course_id(course_id)
        if parsed_id is None:
            raise HTTPException(status_code=404, detail="deliverable not found")

        with SessionLocal() as session:
            record = (
                session.query(CourseProjectVersionModel)
                .filter(CourseProjectVersionModel.course_id == parsed_id)
                .order_by(CourseProjectVersionModel.version_no.desc())
                .first()
            )
        if record is None:
            raise HTTPException(status_code=404, detail="deliverable not found")
        payload = json.loads(record.snapshot_json)
        return {"course_id": course_id, "lesson_plan": payload["lesson_plan"]}

    def regenerate_section(self, course_id: str, section: str) -> dict:
        latest = self.get_latest(course_id)
        lesson_plan = latest["lesson_plan"]

        if section == "timeline":
            lesson_plan["timeline"] = [{"phase": "导入", "minutes": 8, "regenerated": True}]
        else:
            lesson_plan[section] = {"regenerated": True}

        return self._create_version(course_id, lesson_plan, source=f"regenerate:{section}")


    def _create_version(self, course_id: str, lesson_plan: dict, source: str) -> dict:
        parsed_id = _parse_course_id(course_id)
        if parsed_id is None:
            raise HTTPException(status_code=404, detail="course not found")

        with SessionLocal() as session:
            current_max = (
                session.query(CourseProjectVersionModel.version_no)
                .filter(CourseProjectVersionModel.course_id == parsed_id)
                .order_by(CourseProjectVersionModel.version_no.desc())
                .first()
            )
            next_version = 1 if current_max is None else current_max[0] + 1
            snapshot_json = json.dumps({"lesson_plan": lesson_plan}, ensure_ascii=False)
            session.add(
                CourseProjectVersionModel(
                    course_id=parsed_id,
                    version_no=next_version,
                    source=source,
                    snapshot_json=snapshot_json,
                )
            )
            session.commit()
        return {"course_id": course_id, "lesson_plan": lesson_plan}


_deliverable_service = SqlDeliverableService()


def get_deliverable_service() -> SqlDeliverableService:
    return _deliverable_service


def _parse_course_id(course_id: str) -> int | None:
    try:
        return int(course_id)
    except ValueError:
        return None
