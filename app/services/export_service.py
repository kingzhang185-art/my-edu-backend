from uuid import uuid4

from app.core.error_codes import ErrorCode
from app.core.exceptions import AppError
from app.db.models import ExportRecordModel
from app.db.session import SessionLocal
from app.services.deliverable_service import get_deliverable_service


class SqlExportService:
    def create_export(self, course_id: str, fmt: str) -> dict[str, str]:
        if fmt not in {"pdf", "word"}:
            raise AppError(
                status_code=400,
                code=ErrorCode.UNSUPPORTED_EXPORT_FORMAT,
                message="unsupported export format",
            )

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
        parsed_course_id = _parse_course_id(course_id)
        if parsed_course_id is None:
            raise AppError(
                status_code=404,
                code=ErrorCode.COURSE_NOT_FOUND,
                message="course not found",
            )

        with SessionLocal() as session:
            session.add(
                ExportRecordModel(
                    id=export_id,
                    course_id=parsed_course_id,
                    format=fmt,
                    status="success",
                    markdown=markdown,
                    download_url=record["download_url"],
                )
            )
            session.commit()

        return {"export_id": export_id, "download_url": record["download_url"]}

    @staticmethod
    def _compose_markdown(lesson_plan: dict) -> str:
        # TODO: Replace with real docx/pdf adapter.
        lines = ["# 教案导出", "", "## 时间线"]
        for item in lesson_plan.get("timeline", []):
            lines.append(f"- {item}")
        return "\n".join(lines)


_export_service = SqlExportService()


def get_export_service() -> SqlExportService:
    return _export_service


def _parse_course_id(course_id: str) -> int | None:
    try:
        return int(course_id)
    except ValueError:
        return None
