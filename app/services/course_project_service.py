from fastapi import HTTPException

from app.models.course_project import CourseProject
from app.repositories.course_project_repo import InMemoryCourseProjectRepo
from app.schemas.course_project import CreateCourseRequest


class CourseProjectService:
    def __init__(self, repo: InMemoryCourseProjectRepo) -> None:
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
            raise HTTPException(status_code=404, detail="course not found")
        return course
