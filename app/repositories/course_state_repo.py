from app.schemas.course_state import CourseState


class InMemoryCourseStateRepo:
    def __init__(self) -> None:
        self._snapshots: dict[str, CourseState] = {}

    def save(self, course_id: str, state: CourseState) -> None:
        self._snapshots[course_id] = state

    def get(self, course_id: str) -> CourseState | None:
        return self._snapshots.get(course_id)
