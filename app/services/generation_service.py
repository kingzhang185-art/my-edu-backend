from uuid import uuid4

from fastapi import HTTPException

from app.tasks.generation_tasks import GenerationTask


class InMemoryGenerationService:
    def __init__(self) -> None:
        self._tasks: dict[str, GenerationTask] = {}
        self._progress: dict[str, int] = {}

    def start_task(self, course_id: str) -> GenerationTask:
        task_id = str(uuid4())
        progress_key = f"task:progress:{task_id}"
        task = GenerationTask(id=task_id, course_id=course_id, status="pending", progress_key=progress_key)
        self._tasks[task_id] = task
        self._progress[progress_key] = 0
        return task

    def get_task(self, task_id: str) -> GenerationTask:
        task = self._tasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="task not found")
        return task


_generation_service = InMemoryGenerationService()


def get_generation_service() -> InMemoryGenerationService:
    return _generation_service
