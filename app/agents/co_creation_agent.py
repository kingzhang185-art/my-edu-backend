from app.schemas.course_state import CourseState


def ask_next_question(course_state: CourseState, message: str) -> dict[str, str]:
    return {
        "assistant_reply": "好的，我先了解学段和时长。",
        "next_question": "这节课是几年级，时长多少分钟？",
    }
