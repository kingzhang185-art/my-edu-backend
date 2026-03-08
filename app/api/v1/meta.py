from fastapi import APIRouter

from app.core.error_codes import list_error_codes

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])


@router.get("/error-codes")
def get_error_codes() -> dict[str, str]:
    return list_error_codes()
