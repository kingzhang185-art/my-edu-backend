from uuid import uuid4
import json

from fastapi import HTTPException

from app.db.models import GenerationTaskItemModel, GenerationTaskModel
from app.db.session import SessionLocal
from app.tasks.generation_tasks import GenerationTask


class SqlGenerationService:
    def start_task(self, course_id: str, item_keys: list[str] | None = None) -> GenerationTask:
        parsed_course_id = _parse_course_id(course_id)
        if parsed_course_id is None:
            raise HTTPException(status_code=404, detail="course not found")

        keys = item_keys or ["lesson_plan"]
        task_id = str(uuid4())
        progress_key = f"task:progress:{task_id}"
        with SessionLocal() as session:
            session.add(
                GenerationTaskModel(
                    id=task_id,
                    course_id=parsed_course_id,
                    status="pending",
                    progress_key=progress_key,
                )
            )
            session.flush()
            for item_key in keys:
                session.add(
                    GenerationTaskItemModel(
                        task_id=task_id,
                        item_key=item_key,
                        status="pending",
                    )
                )
            session.commit()
        task = GenerationTask(id=task_id, course_id=course_id, status="pending", progress_key=progress_key)
        return task

    def get_task(self, task_id: str) -> GenerationTask:
        with SessionLocal() as session:
            record = session.get(GenerationTaskModel, task_id)
            if record is None:
                raise HTTPException(status_code=404, detail="task not found")
            return GenerationTask(
                id=record.id,
                course_id=str(record.course_id),
                status=record.status,
                progress_key=record.progress_key,
            )

    def update_task_status(self, task_id: str, status: str, error_message: str | None = None) -> None:
        with SessionLocal() as session:
            record = session.get(GenerationTaskModel, task_id)
            if record is None:
                raise HTTPException(status_code=404, detail="task not found")
            record.status = status
            record.error_message = error_message
            session.commit()

    def update_task_item(
        self,
        task_id: str,
        item_key: str,
        status: str,
        output: dict | None = None,
        error_message: str | None = None,
    ) -> None:
        with SessionLocal() as session:
            item = (
                session.query(GenerationTaskItemModel)
                .filter(GenerationTaskItemModel.task_id == task_id)
                .filter(GenerationTaskItemModel.item_key == item_key)
                .first()
            )
            if item is None:
                raise HTTPException(status_code=404, detail=f"task item not found: {item_key}")
            item.status = status
            item.error_message = error_message
            item.output_json = None if output is None else json.dumps(output, ensure_ascii=False)
            session.commit()


_generation_service = SqlGenerationService()


def get_generation_service() -> SqlGenerationService:
    return _generation_service


def _parse_course_id(course_id: str) -> int | None:
    try:
        return int(course_id)
    except ValueError:
        return None
