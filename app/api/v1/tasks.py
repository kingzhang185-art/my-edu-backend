from fastapi import APIRouter

from app.services.generation_service import get_generation_service

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("/{task_id}")
def get_task(task_id: str) -> dict[str, str]:
    task = get_generation_service().get_task(task_id)
    return {
        "task_id": task.id,
        "course_id": task.course_id,
        "status": task.status,
        "progress_key": task.progress_key,
    }
