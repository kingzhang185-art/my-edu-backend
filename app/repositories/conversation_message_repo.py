from typing import Protocol

from sqlalchemy.orm import Session, sessionmaker

from app.db.models import ConversationMessageModel


class ConversationMessageRepo(Protocol):
    def append(self, course_id: str, role: str, content: str) -> None: ...

    def list_by_course(self, course_id: str) -> list[dict[str, str]]: ...


class InMemoryConversationMessageRepo:
    """Mongo placeholder repository for conversation history."""

    def __init__(self) -> None:
        self._messages: dict[str, list[dict[str, str]]] = {}

    def append(self, course_id: str, role: str, content: str) -> None:
        self._messages.setdefault(course_id, []).append({"role": role, "content": content})

    def list_by_course(self, course_id: str) -> list[dict[str, str]]:
        return list(self._messages.get(course_id, []))


class SqlAlchemyConversationMessageRepo:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def append(self, course_id: str, role: str, content: str) -> None:
        parsed_id = _parse_course_id(course_id)
        if parsed_id is None:
            raise ValueError(f"invalid course id: {course_id}")
        with self._session_factory() as session:
            record = ConversationMessageModel(course_id=parsed_id, role=role, content=content)
            session.add(record)
            session.commit()

    def list_by_course(self, course_id: str) -> list[dict[str, str]]:
        parsed_id = _parse_course_id(course_id)
        if parsed_id is None:
            return []

        with self._session_factory() as session:
            rows = (
                session.query(ConversationMessageModel)
                .filter(ConversationMessageModel.course_id == parsed_id)
                .order_by(ConversationMessageModel.id.asc())
                .all()
            )
            return [{"role": row.role, "content": row.content} for row in rows]


def _parse_course_id(course_id: str) -> int | None:
    try:
        return int(course_id)
    except ValueError:
        return None
