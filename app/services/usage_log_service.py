import json
from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from app.db.models import UsageLogModel


class UsageLogService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def log(self, event_type: str, course_id: str | None = None, payload: dict[str, Any] | None = None) -> None:
        parsed_course_id: int | None = None
        if course_id is not None:
            try:
                parsed_course_id = int(course_id)
            except ValueError:
                parsed_course_id = None

        payload_json = None
        if payload is not None:
            payload_json = json.dumps(payload, ensure_ascii=False)

        with self._session_factory() as session:
            session.add(
                UsageLogModel(
                    course_id=parsed_course_id,
                    event_type=event_type,
                    payload_json=payload_json,
                )
            )
            session.commit()
