from fastapi import APIRouter, status

from app.agents.orchestrator import get_agent_orchestrator
from app.core.error_codes import ErrorCode
from app.core.exceptions import AppError
from app.db.models import CoursePlanOptionModel
from app.db.session import SessionLocal
from app.models.course_project import CourseProject
from app.repositories.course_project_repo import SqlAlchemyCourseProjectRepo
from app.schemas.course_project import CourseProjectResponse, CreateCourseRequest
from app.schemas.plan_option import ConfirmPlanRequest
from app.services.course_project_service import CourseProjectService
from app.services.usage_log_service import UsageLogService

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])

_repo = SqlAlchemyCourseProjectRepo(SessionLocal)
_service = CourseProjectService(_repo)
_usage_log_service = UsageLogService(SessionLocal)


def get_course_service() -> CourseProjectService:
    return _service


def _to_response(course: CourseProject) -> CourseProjectResponse:
    return CourseProjectResponse.model_validate(course.__dict__)


@router.post("", response_model=CourseProjectResponse, status_code=status.HTTP_201_CREATED)
def create_course(payload: CreateCourseRequest) -> CourseProjectResponse:
    course = _service.create(payload)
    _usage_log_service.log("course_created", course.id, payload.model_dump())
    return _to_response(course)


@router.get("/{course_id}", response_model=CourseProjectResponse)
def get_course(course_id: str) -> CourseProjectResponse:
    course = _service.get_or_404(course_id)
    return _to_response(course)


@router.post("/{course_id}/plan-options")
def create_plan_options(course_id: str) -> dict[str, list[dict[str, str]]]:
    course = _service.get_or_404(course_id)
    options = get_agent_orchestrator().build_plan_options(course)
    _service.save(course)
    _replace_plan_options(course_id, options["items"])
    _usage_log_service.log("plan_options_generated", course_id, {"count": len(options["items"])})
    return options


@router.post("/{course_id}/confirm-plan", response_model=CourseProjectResponse)
def confirm_plan(course_id: str, payload: ConfirmPlanRequest) -> CourseProjectResponse:
    course = _service.get_or_404(course_id)
    selected = _get_plan_option(course_id, payload.option_id)
    if selected is None:
        return _to_response(course)

    course.selected_option_id = payload.option_id
    course.stage = "plan_confirmed"
    _service.save(course)
    _usage_log_service.log("plan_confirmed", course_id, {"option_id": payload.option_id})
    return _to_response(course)


@router.post("/{course_id}/generate-lesson-plan", status_code=status.HTTP_202_ACCEPTED)
def generate_lesson_plan(course_id: str) -> dict[str, str]:
    course = _service.get_or_404(course_id)
    if course.stage != "plan_confirmed":
        raise AppError(
            status_code=400,
            code=ErrorCode.PLAN_NOT_CONFIRMED,
            message="plan not confirmed",
        )

    task = get_agent_orchestrator().run_generation_pipeline(course)
    _service.save(course)
    _usage_log_service.log("generation_started", course_id, {"task_id": task.id})
    return {"task_id": task.id}


def _replace_plan_options(course_id: str, items: list[dict[str, str]]) -> None:
    parsed_course_id = int(course_id)
    with SessionLocal() as session:
        session.query(CoursePlanOptionModel).filter(
            CoursePlanOptionModel.course_id == parsed_course_id
        ).delete()
        for item in items:
            session.add(
                CoursePlanOptionModel(
                    course_id=parsed_course_id,
                    option_key=item["id"],
                    label=item["label"],
                )
            )
        session.commit()


def _get_plan_option(course_id: str, option_id: str) -> CoursePlanOptionModel | None:
    parsed_course_id = int(course_id)
    with SessionLocal() as session:
        return (
            session.query(CoursePlanOptionModel)
            .filter(CoursePlanOptionModel.course_id == parsed_course_id)
            .filter(CoursePlanOptionModel.option_key == option_id)
            .first()
        )
