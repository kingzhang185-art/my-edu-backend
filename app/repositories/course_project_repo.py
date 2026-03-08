from typing import Protocol

from sqlalchemy.orm import Session, sessionmaker

from app.db.models import CourseProjectModel
from app.models.course_project import CourseProject


class CourseProjectRepo(Protocol):
    def create(self, topic: str, subject: str, grade: str, duration: int) -> CourseProject: ...

    def get(self, course_id: str) -> CourseProject | None: ...

    def save(self, course: CourseProject) -> CourseProject: ...


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

    def save(self, course: CourseProject) -> CourseProject:
        self._store[course.id] = course
        return course


def _to_domain(record: CourseProjectModel) -> CourseProject:
    return CourseProject(
        id=str(record.id),
        topic=record.topic,
        subject=record.subject,
        grade=record.grade,
        duration=record.duration,
        stage=record.stage,
        selected_option_id=record.selected_option_id,
    )


class SqlAlchemyCourseProjectRepo:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, topic: str, subject: str, grade: str, duration: int) -> CourseProject:
        with self._session_factory() as session:
            record = CourseProjectModel(
                topic=topic,
                subject=subject,
                grade=grade,
                duration=duration,
                stage="draft",
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return _to_domain(record)

    def get(self, course_id: str) -> CourseProject | None:
        record_id = _parse_id(course_id)
        if record_id is None:
            return None

        with self._session_factory() as session:
            record = session.get(CourseProjectModel, record_id)
            if record is None:
                return None
            return _to_domain(record)

    def save(self, course: CourseProject) -> CourseProject:
        record_id = _parse_id(course.id)
        if record_id is None:
            raise ValueError(f"invalid course id: {course.id}")

        with self._session_factory() as session:
            record = session.get(CourseProjectModel, record_id)
            if record is None:
                raise ValueError(f"course id not found: {course.id}")

            record.topic = course.topic
            record.subject = course.subject
            record.grade = course.grade
            record.duration = course.duration
            record.stage = course.stage
            record.selected_option_id = course.selected_option_id
            session.commit()
            session.refresh(record)
            return _to_domain(record)


def _parse_id(course_id: str) -> int | None:
    try:
        return int(course_id)
    except ValueError:
        return None
