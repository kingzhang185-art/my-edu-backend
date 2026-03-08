from fastapi import APIRouter

from app.agents.orchestrator import get_agent_orchestrator
from app.api.v1.courses import get_course_service
from app.db.session import SessionLocal
from app.repositories.conversation_message_repo import SqlAlchemyConversationMessageRepo
from app.schemas.chat import ChatRequest
from app.services.usage_log_service import UsageLogService

router = APIRouter(prefix="/api/v1/courses", tags=["chat"])
_message_repo = SqlAlchemyConversationMessageRepo(SessionLocal)
_usage_log_service = UsageLogService(SessionLocal)


@router.post("/{course_id}/chat")
def chat(course_id: str, payload: ChatRequest) -> dict[str, str]:
    course_service = get_course_service()
    course = course_service.get_or_404(course_id)
    _message_repo.append(course_id, "user", payload.message)

    result = get_agent_orchestrator().run_clarification(course, payload.message)
    course_service.save(course)

    _message_repo.append(course_id, "assistant", result["assistant_reply"])
    _usage_log_service.log("chat_message", course_id, {"message_length": len(payload.message)})
    return result
