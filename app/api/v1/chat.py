from fastapi import APIRouter

from app.api.v1.courses import get_course_service
from app.db.session import SessionLocal
from app.repositories.conversation_message_repo import SqlAlchemyConversationMessageRepo
from app.schemas.chat import ChatRequest
from app.schemas.course_state import CourseState
from app.services.usage_log_service import UsageLogService
from app.workflows.clarify_workflow import run_clarification

router = APIRouter(prefix="/api/v1/courses", tags=["chat"])
_message_repo = SqlAlchemyConversationMessageRepo(SessionLocal)
_usage_log_service = UsageLogService(SessionLocal)


@router.post("/{course_id}/chat")
def chat(course_id: str, payload: ChatRequest) -> dict[str, str]:
    course = get_course_service().get_or_404(course_id)
    _message_repo.append(course_id, "user", payload.message)

    state = CourseState(
        topic=course.topic,
        subject=course.subject,
        grade=course.grade,
        duration=course.duration,
    )
    result = run_clarification(state, payload.message)

    _message_repo.append(course_id, "assistant", result["assistant_reply"])
    _usage_log_service.log("chat_message", course_id, {"message_length": len(payload.message)})
    return result
