class InMemoryConversationMessageRepo:
    """Mongo placeholder repository for conversation history."""

    def __init__(self) -> None:
        self._messages: dict[str, list[dict[str, str]]] = {}

    def append(self, course_id: str, role: str, content: str) -> None:
        self._messages.setdefault(course_id, []).append({"role": role, "content": content})

    def list_by_course(self, course_id: str) -> list[dict[str, str]]:
        return list(self._messages.get(course_id, []))
