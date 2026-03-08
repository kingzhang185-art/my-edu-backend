from fastapi import HTTPException


class InMemoryDeliverableService:
    def __init__(self) -> None:
        self._deliverables: dict[str, dict] = {}

    def upsert_placeholder(self, course_id: str) -> dict:
        lesson_plan = {
            "meta": {"course_id": course_id},
            "objectives": [],
            "timeline": [{"phase": "导入", "minutes": 5}],
            "teacher_script": [],
            "board_plan": "",
            "exercises": [],
        }
        record = {"course_id": course_id, "lesson_plan": lesson_plan}
        self._deliverables[course_id] = record
        return record

    def get_latest(self, course_id: str) -> dict:
        record = self._deliverables.get(course_id)
        if record is None:
            raise HTTPException(status_code=404, detail="deliverable not found")
        return record

    def regenerate_section(self, course_id: str, section: str) -> dict:
        record = self.get_latest(course_id)
        lesson_plan = record["lesson_plan"]

        if section == "timeline":
            lesson_plan["timeline"] = [{"phase": "导入", "minutes": 8, "regenerated": True}]
        else:
            lesson_plan[section] = {"regenerated": True}

        return record


_deliverable_service = InMemoryDeliverableService()


def get_deliverable_service() -> InMemoryDeliverableService:
    return _deliverable_service
