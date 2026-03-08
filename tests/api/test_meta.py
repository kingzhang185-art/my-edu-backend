from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.services.model_gateway import is_valid_model_gateway_key


client = TestClient(app)


def test_error_codes_endpoint_exposes_business_codes() -> None:
    response = client.get("/api/v1/meta/error-codes")

    assert response.status_code == 200
    body = response.json()
    assert body["TASK_NOT_FOUND"] == "task_not_found"
    assert body["PLAN_NOT_CONFIRMED"] == "plan_not_confirmed"


def test_model_gateway_endpoint_reports_runtime_config() -> None:
    response = client.get("/api/v1/meta/model-gateway")

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == settings.model_gateway_provider
    assert body["model"] == settings.model_gateway_model
    assert body["base_url"] == settings.model_gateway_base_url
    assert body["timeout_seconds"] == settings.model_gateway_timeout_seconds
    expected_key_configured = is_valid_model_gateway_key(
        settings.model_gateway_provider,
        settings.model_gateway_api_key,
    )
    assert body["key_configured"] is expected_key_configured
    assert body["ready"] is expected_key_configured
