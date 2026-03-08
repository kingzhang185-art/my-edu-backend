import json
import logging
from typing import Protocol

import httpx

from app.agents.prompt_protocol import PromptSpec
from app.core.config import settings

logger = logging.getLogger("app.model_gateway")


class ModelGateway(Protocol):
    def generate_json(self, spec: PromptSpec) -> dict: ...


class DeepSeekModelGateway:
    def __init__(
        self,
        *,
        provider: str,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: int,
    ) -> None:
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate_json(self, spec: PromptSpec) -> dict:
        if self.provider != "deepseek":
            return {}
        if not self._has_valid_key():
            return {}

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": spec.system_prompt},
                {"role": "user", "content": spec.user_prompt},
            ],
            "response_format": spec.response_format,
            "max_tokens": spec.max_tokens,
            "temperature": 0.3,
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
        except Exception as exc:
            logger.warning(
                "model gateway request failed, fallback to local agent output",
                extra={"provider": self.provider, "model": self.model, "error": str(exc)},
            )
            return {}

        return _parse_chat_completion_json(body)

    def _has_valid_key(self) -> bool:
        return is_valid_model_gateway_key(self.provider, self.api_key)


def _parse_chat_completion_json(body: dict) -> dict:
    choices = body.get("choices", [])
    if not choices:
        return {}
    message = choices[0].get("message", {})
    content = message.get("content")
    if isinstance(content, dict):
        return content
    if not isinstance(content, str) or not content.strip():
        return {}
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return parsed


_gateway: ModelGateway | None = None


def get_model_gateway() -> ModelGateway:
    global _gateway
    if _gateway is None:
        _gateway = DeepSeekModelGateway(
            provider=settings.model_gateway_provider,
            api_key=settings.model_gateway_api_key,
            base_url=settings.model_gateway_base_url,
            model=settings.model_gateway_model,
            timeout_seconds=settings.model_gateway_timeout_seconds,
        )
    return _gateway


def is_valid_model_gateway_key(provider: str, api_key: str) -> bool:
    if provider != "deepseek":
        return False
    key = api_key.strip()
    if not key:
        return False
    if key in {"replace-me", "your-deepseek-sk"}:
        return False
    return key.startswith("sk-")


def get_model_gateway_meta() -> dict[str, object]:
    key_configured = is_valid_model_gateway_key(
        settings.model_gateway_provider,
        settings.model_gateway_api_key,
    )
    return {
        "provider": settings.model_gateway_provider,
        "model": settings.model_gateway_model,
        "base_url": settings.model_gateway_base_url,
        "timeout_seconds": settings.model_gateway_timeout_seconds,
        "key_configured": key_configured,
        "ready": key_configured,
    }
