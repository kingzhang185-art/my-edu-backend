from pydantic import BaseModel, Field


class CourseState(BaseModel):
    topic: str
    subject: str
    grade: str
    duration: int
    teaching_style: str | None = None
    deliverables: list[str] = Field(default_factory=list)
