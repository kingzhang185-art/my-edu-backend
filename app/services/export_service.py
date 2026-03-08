from uuid import uuid4

from fastapi import HTTPException

from app.services.deliverable_service import get_deliverable_service


class InMemoryExportService:
    def __init__(self) -> None:
        self._exports: dict[str, dict] = {}

    def create_export(self, course_id: str, fmt: str) -> dict[str, str]:
        if fmt not in {"pdf", "word"}:
            raise HTTPException(status_code=400, detail="unsupported export format")

        latest = get_deliverable_service().get_latest(course_id)
        lesson_plan = latest["lesson_plan"]
        markdown = self._compose_markdown(lesson_plan)

        export_id = str(uuid4())
        record = {
            "export_id": export_id,
            "course_id": course_id,
            "format": fmt,
            "markdown": markdown,
            "download_url": f"https://example.com/exports/{export_id}.{fmt}",
        }
        self._exports[export_id] = record
        return {"export_id": export_id, "download_url": record["download_url"]}

    @staticmethod
    def _compose_markdown(lesson_plan: dict) -> str:
        # TODO: Replace with real docx/pdf adapter.
        lines = ["# 教案导出", "", "## 时间线"]
        for item in lesson_plan.get("timeline", []):
            lines.append(f"- {item}")
        return "\n".join(lines)


_export_service = InMemoryExportService()


def get_export_service() -> InMemoryExportService:
    return _export_service
