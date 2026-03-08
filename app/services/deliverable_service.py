import json

from app.core.error_codes import ErrorCode
from app.core.exceptions import AppError
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

    def upsert_generated(self, course_id: str, lesson_plan: dict, quality_report: dict) -> dict:
        payload = dict(lesson_plan)
        payload["quality_report"] = quality_report
        return self._create_version(course_id, payload, source="generate")

    def get_latest(self, course_id: str) -> dict:
        parsed_id = _parse_course_id(course_id)
        if parsed_id is None:
            raise AppError(
                status_code=404,
                code=ErrorCode.DELIVERABLE_NOT_FOUND,
                message="deliverable not found",
            )

        with SessionLocal() as session:
            record = (
                session.query(CourseProjectVersionModel)
                .filter(CourseProjectVersionModel.course_id == parsed_id)
                .order_by(CourseProjectVersionModel.version_no.desc())
                .first()
            )
        if record is None:
            raise AppError(
                status_code=404,
                code=ErrorCode.DELIVERABLE_NOT_FOUND,
                message="deliverable not found",
            )
        payload = json.loads(record.snapshot_json)
        return {"course_id": course_id, "lesson_plan": payload["lesson_plan"]}

    def regenerate_section(self, course_id: str, section: str) -> dict:
        latest = self.get_latest(course_id)
        lesson_plan = latest["lesson_plan"]

        if section == "timeline":
            lesson_plan["timeline"] = [{"phase": "导入", "minutes": 8, "regenerated": True}]
        elif section == "exercises":
            lesson_plan["exercises"] = ["已重新生成练习题（示例）"]
        elif section == "board_plan":
            lesson_plan["board_plan"] = "已重新生成板书设计（示例）"
        elif section == "objectives":
            lesson_plan["objectives"] = ["已重新生成教学目标（示例）"]
        elif section == "teacher_script":
            lesson_plan["teacher_script"] = ["已重新生成教师讲稿（示例）"]
        else:
            lesson_plan[section] = {"regenerated": True}

        return self._create_version(course_id, lesson_plan, source=f"regenerate:{section}")


    def _create_version(self, course_id: str, lesson_plan: dict, source: str) -> dict:
        parsed_id = _parse_course_id(course_id)
        if parsed_id is None:
            raise AppError(
                status_code=404,
                code=ErrorCode.COURSE_NOT_FOUND,
                message="course not found",
            )

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
