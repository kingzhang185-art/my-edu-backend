from fastapi import APIRouter

from app.api.v1.courses import get_course_service
from app.services.deliverable_service import get_deliverable_service

router = APIRouter(prefix="/api/v1/courses", tags=["deliverables"])


@router.get("/{course_id}/deliverables/latest")
def get_latest_deliverable(course_id: str) -> dict:
    get_course_service().get_or_404(course_id)
    return get_deliverable_service().get_latest(course_id)


@router.post("/{course_id}/deliverables/{section}/regenerate")
def regenerate_deliverable_section(course_id: str, section: str) -> dict:
    get_course_service().get_or_404(course_id)
    return get_deliverable_service().regenerate_section(course_id, section)
