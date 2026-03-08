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
