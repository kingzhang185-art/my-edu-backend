from dataclasses import dataclass


@dataclass
class CourseProject:
    id: str
    topic: str
    subject: str
    grade: str
    duration: int
    stage: str = "draft"
    selected_option_id: str | None = None
