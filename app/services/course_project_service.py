from app.core.error_codes import ErrorCode
from app.core.exceptions import AppError
from app.models.course_project import CourseProject
from app.repositories.course_project_repo import CourseProjectRepo
from app.schemas.course_project import CreateCourseRequest


class CourseProjectService:
    def __init__(self, repo: CourseProjectRepo) -> None:
        self._repo = repo

    def create(self, request: CreateCourseRequest) -> CourseProject:
        return self._repo.create(
            topic=request.topic,
            subject=request.subject,
            grade=request.grade,
            duration=request.duration,
        )

    def get_or_404(self, course_id: str) -> CourseProject:
        course = self._repo.get(course_id)
        if course is None:
            raise AppError(
                status_code=404,
                code=ErrorCode.COURSE_NOT_FOUND,
                message="course not found",
            )
        return course

    def save(self, course: CourseProject) -> CourseProject:
        return self._repo.save(course)
