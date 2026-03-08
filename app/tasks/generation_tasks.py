from dataclasses import dataclass


@dataclass
class GenerationTask:
    id: str
    course_id: str
    status: str
    progress_key: str
