from fastapi import APIRouter, status

from app.models.course_project import CourseProject
from app.repositories.course_project_repo import InMemoryCourseProjectRepo
from app.schemas.course_project import CourseProjectResponse, CreateCourseRequest
from app.schemas.plan_option import ConfirmPlanRequest
from app.services.course_project_service import CourseProjectService
from app.workflows.plan_options_workflow import generate_plan_options

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])

_repo = InMemoryCourseProjectRepo()
_service = CourseProjectService(_repo)
_plan_options_by_course: dict[str, list[dict[str, str]]] = {}


def get_course_service() -> CourseProjectService:
    return _service


def _to_response(course: CourseProject) -> CourseProjectResponse:
    return CourseProjectResponse.model_validate(course.__dict__)


@router.post("", response_model=CourseProjectResponse, status_code=status.HTTP_201_CREATED)
def create_course(payload: CreateCourseRequest) -> CourseProjectResponse:
    course = _service.create(payload)
    return _to_response(course)


@router.get("/{course_id}", response_model=CourseProjectResponse)
def get_course(course_id: str) -> CourseProjectResponse:
    course = _service.get_or_404(course_id)
    return _to_response(course)


@router.post("/{course_id}/plan-options")
def create_plan_options(course_id: str) -> dict[str, list[dict[str, str]]]:
    course = _service.get_or_404(course_id)
    options = generate_plan_options(course)
    _plan_options_by_course[course_id] = options["items"]
    return options


@router.post("/{course_id}/confirm-plan", response_model=CourseProjectResponse)
def confirm_plan(course_id: str, payload: ConfirmPlanRequest) -> CourseProjectResponse:
    course = _service.get_or_404(course_id)
    options = _plan_options_by_course.get(course_id, [])
    selected = next((item for item in options if item["id"] == payload.option_id), None)
    if selected is None:
        return _to_response(course)

    course.selected_option_id = payload.option_id
    course.stage = "plan_confirmed"
    return _to_response(course)
