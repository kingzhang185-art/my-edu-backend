import json

from app.agents.prompt_protocol import PromptSpec
from app.services.model_gateway import DeepSeekModelGateway


def _spec() -> PromptSpec:
    return PromptSpec(
        agent="lesson_plan",
        stage="generation",
        system_prompt="Return JSON only.",
        user_prompt="Generate lesson plan.",
        output_schema={"timeline": [{"phase": "string", "minutes": "int"}]},
        response_format={"type": "json_object"},
        max_tokens=512,
    )


def test_gateway_returns_empty_when_api_key_missing():
    gateway = DeepSeekModelGateway(
        provider="deepseek",
        api_key="",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        timeout_seconds=3,
    )
    assert gateway.generate_json(_spec()) == {}


def test_gateway_parses_json_response(monkeypatch):
    class _Resp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": '{"assistant_reply":"ok"}'}}]}

    class _Client:
        def __enter__(self):
            return self

        def __exit__(self, _exc_type, _exc, _tb):
            return False

        def post(self, *_args, **_kwargs):
            return _Resp()

    monkeypatch.setattr("app.services.model_gateway.httpx.Client", lambda **_kwargs: _Client())

    gateway = DeepSeekModelGateway(
        provider="deepseek",
        api_key="sk-test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        timeout_seconds=3,
    )
    payload = gateway.generate_json(_spec())
    assert payload == {"assistant_reply": "ok"}


def test_gateway_request_uses_json_response_format(monkeypatch):
    captured: dict = {}

    class _Resp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": json.dumps({"ok": True})}}]}

    class _Client:
        def __enter__(self):
            return self

        def __exit__(self, _exc_type, _exc, _tb):
            return False

        def post(self, _url, **kwargs):
            captured.update(kwargs.get("json", {}))
            return _Resp()

    monkeypatch.setattr("app.services.model_gateway.httpx.Client", lambda **_kwargs: _Client())

    gateway = DeepSeekModelGateway(
        provider="deepseek",
        api_key="sk-test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        timeout_seconds=3,
    )
    _ = gateway.generate_json(_spec())

    assert captured["response_format"] == {"type": "json_object"}
    assert captured["model"] == "deepseek-chat"
