from app.models.course_project import CourseProject


class InMemoryCourseProjectRepo:
    def __init__(self) -> None:
        self._store: dict[str, CourseProject] = {}
        self._next_id = 1

    def create(self, topic: str, subject: str, grade: str, duration: int) -> CourseProject:
        course = CourseProject(
            id=str(self._next_id),
            topic=topic,
            subject=subject,
            grade=grade,
            duration=duration,
        )
        self._store[course.id] = course
        self._next_id += 1
        return course

    def get(self, course_id: str) -> CourseProject | None:
        return self._store.get(course_id)
