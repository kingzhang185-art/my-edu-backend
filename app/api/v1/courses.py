from fastapi import APIRouter, status

from app.repositories.course_project_repo import InMemoryCourseProjectRepo
from app.schemas.course_project import CourseProjectResponse, CreateCourseRequest
from app.services.course_project_service import CourseProjectService

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])

_repo = InMemoryCourseProjectRepo()
_service = CourseProjectService(_repo)


@router.post("", response_model=CourseProjectResponse, status_code=status.HTTP_201_CREATED)
def create_course(payload: CreateCourseRequest) -> CourseProjectResponse:
    course = _service.create(payload)
    return CourseProjectResponse.model_validate(course.__dict__)


@router.get("/{course_id}", response_model=CourseProjectResponse)
def get_course(course_id: str) -> CourseProjectResponse:
    course = _service.get_or_404(course_id)
    return CourseProjectResponse.model_validate(course.__dict__)
