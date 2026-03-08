from fastapi import APIRouter

from app.core.error_codes import list_error_codes
from app.services.model_gateway import get_model_gateway_meta

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])


@router.get("/error-codes")
def get_error_codes() -> dict[str, str]:
    return list_error_codes()


@router.get("/model-gateway")
def get_model_gateway() -> dict[str, object]:
    return get_model_gateway_meta()
