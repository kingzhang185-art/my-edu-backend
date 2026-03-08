from app.schemas.course_state import CourseState
from app.agents.prompt_protocol import PromptSpec, build_co_creation_prompt
from app.services.model_gateway import get_model_gateway


def ask_next_question(course_state: CourseState, message: str) -> dict[str, str]:
    spec = get_prompt_spec(course_state, message)
    llm_payload = get_model_gateway().generate_json(spec)
    llm_reply = _parse_llm_reply(llm_payload)
    if llm_reply is not None:
        return llm_reply
    return {
        "assistant_reply": "好的，我先了解学段和时长。",
        "next_question": "这节课是几年级，时长多少分钟？",
    }


def get_prompt_spec(course_state: CourseState, message: str) -> PromptSpec:
    return build_co_creation_prompt(course_state, message)


def _parse_llm_reply(payload: dict) -> dict[str, str] | None:
    assistant_reply = payload.get("assistant_reply")
    next_question = payload.get("next_question")
    if isinstance(assistant_reply, str) and isinstance(next_question, str):
        if assistant_reply.strip() and next_question.strip():
            return {
                "assistant_reply": assistant_reply.strip(),
                "next_question": next_question.strip(),
            }
    return None
