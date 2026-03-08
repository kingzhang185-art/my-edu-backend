from app.agents.lesson_plan_agent import generate_lesson_plan
from app.models.course_project import CourseProject
from app.schemas.course_state import CourseState
from app.services.deliverable_service import SqlDeliverableService, get_deliverable_service
from app.services.generation_service import SqlGenerationService, get_generation_service
from app.tasks.generation_tasks import GenerationTask
from app.workflows.clarify_workflow import run_clarification
from app.workflows.plan_options_workflow import generate_plan_options
from app.workflows.quality_workflow import run_quality_check


class AgentOrchestrator:
    """Main coordinator that advances stage and runs specialized agents."""

    def __init__(
        self,
        generation_service: SqlGenerationService,
        deliverable_service: SqlDeliverableService,
    ) -> None:
        self._generation_service = generation_service
        self._deliverable_service = deliverable_service

    def run_clarification(self, course: CourseProject, message: str) -> dict[str, str]:
        state = CourseState(
            topic=course.topic,
            subject=course.subject,
            grade=course.grade,
            duration=course.duration,
        )
        result = run_clarification(state, message)
        if course.stage == "draft":
            course.stage = "clarifying"
        return result

    def build_plan_options(self, course: CourseProject) -> dict[str, list[dict[str, str]]]:
        options = generate_plan_options(course)
        if course.stage in {"draft", "clarifying"}:
            course.stage = "options_ready"
        return options

    def run_generation_pipeline(self, course: CourseProject) -> GenerationTask:
        task = self._generation_service.start_task(
            course_id=course.id,
            item_keys=["lesson_plan", "quality_check"],
        )

        self._generation_service.update_task_status(task.id, "running")
        course.stage = "generating"

        try:
            lesson_plan = generate_lesson_plan(course)
            self._generation_service.update_task_item(
                task_id=task.id,
                item_key="lesson_plan",
                status="success",
                output=lesson_plan,
            )

            quality = run_quality_check(output=lesson_plan, grade=course.grade)
            quality_status = "success" if quality["passed"] else "failed"
            self._generation_service.update_task_item(
                task_id=task.id,
                item_key="quality_check",
                status=quality_status,
                output=quality,
                error_message=None if quality["passed"] else "quality gate failed",
            )

            self._deliverable_service.upsert_generated(course_id=course.id, lesson_plan=lesson_plan, quality_report=quality)

            if quality["passed"]:
                self._generation_service.update_task_status(task.id, "success")
                course.stage = "reviewed"
            else:
                self._generation_service.update_task_status(task.id, "failed", error_message="quality gate failed")
                course.stage = "generated"
            return self._generation_service.get_task(task.id)
        except Exception as exc:
            self._generation_service.update_task_status(task.id, "failed", error_message=str(exc))
            course.stage = "plan_confirmed"
            raise


_orchestrator = AgentOrchestrator(
    generation_service=get_generation_service(),
    deliverable_service=get_deliverable_service(),
)


def get_agent_orchestrator() -> AgentOrchestrator:
    return _orchestrator
