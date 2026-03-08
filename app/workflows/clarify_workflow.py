from app.agents.co_creation_agent import ask_next_question
from app.schemas.course_state import CourseState


def run_clarification(course_state: CourseState, message: str) -> dict[str, str]:
    return ask_next_question(course_state, message)
