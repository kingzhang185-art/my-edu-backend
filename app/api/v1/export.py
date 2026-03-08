from fastapi import APIRouter, status
from pydantic import BaseModel

from app.api.v1.courses import get_course_service
from app.services.export_service import get_export_service

router = APIRouter(prefix="/api/v1/courses", tags=["export"])


class ExportRequest(BaseModel):
    format: str


@router.post("/{course_id}/export", status_code=status.HTTP_202_ACCEPTED)
def export_course(course_id: str, payload: ExportRequest) -> dict[str, str]:
    get_course_service().get_or_404(course_id)
    return get_export_service().create_export(course_id=course_id, fmt=payload.format)
