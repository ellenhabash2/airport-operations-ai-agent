"""
Tests for retrying transient Gemini failures.
"""

import pytest
from google.genai import errors, types

import routes.agent_routes as agent_routes
import services.gemini_service as gemini_service
from services.gemini_service import (
    MAX_ATTEMPTS,
    GeminiService,
    GeminiUnavailableError,
)


def _api_error(code: int) -> errors.APIError:
    """Build an API error carrying the given status code."""
    return errors.APIError(
        code, {"error": {"code": code, "message": "test", "status": "TEST"}}
    )


class FlakyClient:
    """Fails a fixed number of times before succeeding."""

    def __init__(self, failures: int, code: int = 503):
        self.failures = failures
        self.code = code
        self.calls = 0
        self.models = self

    def generate_content(self, model, contents, config):
        self.calls += 1

        if self.calls <= self.failures:
            raise _api_error(self.code)

        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        role="model",
                        parts=[types.Part.from_text(text="recovered")],
                    )
                )
            ]
        )


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    """Skip the backoff delay so the tests stay fast."""
    monkeypatch.setattr(gemini_service.time, "sleep", lambda seconds: None)


def _service_with(client) -> GeminiService:
    """Build a Gemini service backed by the given fake client."""
    service = GeminiService.__new__(GeminiService)
    service.client = client
    service.model = "test-model"
    service.tools = []

    return service


def _contents() -> list[types.Content]:
    return [
        types.Content(role="user", parts=[types.Part.from_text(text="hello")])
    ]


def test_a_transient_failure_is_retried(app):
    """A single 503 is retried and the second attempt is returned."""
    client = FlakyClient(failures=1)
    response = _service_with(client).generate(_contents())

    assert client.calls == 2
    assert response.text == "recovered"


def test_rate_limiting_is_retried(app):
    """429 is treated as transient too."""
    client = FlakyClient(failures=1, code=429)
    response = _service_with(client).generate(_contents())

    assert client.calls == 2
    assert response.text == "recovered"


def test_persistent_failure_raises_a_clear_error(app):
    """After every attempt fails the error names the service, not Google."""
    client = FlakyClient(failures=MAX_ATTEMPTS)

    with pytest.raises(GeminiUnavailableError) as raised:
        _service_with(client).generate(_contents())

    assert client.calls == MAX_ATTEMPTS
    assert "temporarily unavailable" in str(raised.value)


def test_a_permanent_error_is_not_retried(app):
    """A bad request fails immediately instead of being retried."""
    client = FlakyClient(failures=MAX_ATTEMPTS, code=400)

    with pytest.raises(errors.APIError):
        _service_with(client).generate(_contents())

    assert client.calls == 1


def test_the_endpoint_reports_an_unavailable_service(
    client, auth_headers, monkeypatch
):
    """The route answers 503 and flags the failure as retryable."""

    class UnavailableAgent:
        def __init__(self):
            pass

        def chat(self, message, history=None):
            raise GeminiUnavailableError(
                "The AI service is temporarily unavailable."
            )

    monkeypatch.setattr(agent_routes, "AgentService", UnavailableAgent)

    response = client.post(
        "/agent/query", json={"message": "Hello"}, headers=auth_headers
    )
    payload = response.get_json()

    assert response.status_code == 503
    assert payload["retryable"] is True
    assert payload["error"] == "ai service unavailable"