from datetime import datetime

from pydantic import BaseModel


class CreateCourseRequest(BaseModel):
    topic: str
    subject: str
    grade: str
    duration: int


class CourseProjectResponse(BaseModel):
    id: str
    topic: str
    subject: str
    grade: str
    duration: int
    stage: str
    selected_option_id: str | None = None


class UpdateCourseRequest(BaseModel):
    topic: str | None = None
    subject: str | None = None
    grade: str | None = None
    duration: int | None = None


class CourseListItemResponse(BaseModel):
    id: str
    topic: str
    grade: str
    stage: str
    updated_at: datetime
