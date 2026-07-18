"""
Tests for the HTTP layer.
"""

import routes.agent_routes as agent_routes


def test_health_reports_database_status(client):
    """The health check confirms the database is reachable."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["database"] == "ok"


def test_index_lists_the_agent_endpoint(client):
    """The service index advertises the agent endpoint."""
    response = client.get("/")

    assert "/agent/query" in response.get_json()["endpoints"]


def test_register_and_login(client):
    """A user can register and receive a token."""
    registered = client.post(
        "/auth/register",
        json={
            "username": "ops",
            "email": "ops@example.com",
            "password": "password123",
        },
    )
    logged_in = client.post(
        "/auth/login",
        json={"email": "ops@example.com", "password": "password123"},
    )

    assert registered.status_code == 201
    assert logged_in.status_code == 200
    assert "access_token" in logged_in.get_json()


def test_login_with_wrong_password_is_rejected(client):
    """Invalid credentials do not return a token."""
    client.post(
        "/auth/register",
        json={
            "username": "ops",
            "email": "ops@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "ops@example.com", "password": "wrong"},
    )

    assert response.status_code == 401


def test_flights_endpoint_returns_seeded_data(client):
    """The flights endpoint returns the fixtures."""
    response = client.get("/flights")

    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 2


def test_agent_query_requires_a_token(client):
    """
    The agent can write to the database through create_incident, so the
    endpoint must not be reachable anonymously.
    """
    response = client.post("/agent/query", json={"message": "Hello"})

    assert response.status_code == 401


def test_agent_query_rejects_an_empty_message(client, auth_headers):
    """An empty question is refused before the model is called."""
    response = client.post(
        "/agent/query", json={"message": "   "}, headers=auth_headers
    )

    assert response.status_code == 400


def test_agent_query_returns_the_answer_and_tool_calls(
    client, auth_headers, monkeypatch
):
    """A successful query returns the answer and the executed tools."""

    class FakeAgent:
        def __init__(self):
            pass

        def chat(self, message, history=None):
            return {
                "response": "Two flights found.",
                "tool_calls": [
                    {
                        "tool": "get_all_flights",
                        "arguments": {},
                        "failed": False,
                    }
                ],
            }

    monkeypatch.setattr(agent_routes, "AgentService", FakeAgent)

    response = client.post(
        "/agent/query",
        json={"message": "How many flights are there?"},
        headers=auth_headers,
    )
    payload = response.get_json()["data"]

    assert response.status_code == 200
    assert payload["answer"] == "Two flights found."
    assert payload["tool_calls"][0]["tool"] == "get_all_flights"


def test_agent_query_reports_a_missing_api_key(
    client, auth_headers, monkeypatch
):
    """Without a configured key the endpoint reports 503, not 500."""

    class UnconfiguredAgent:
        def __init__(self):
            raise RuntimeError("GEMINI_API_KEY is not configured.")

    monkeypatch.setattr(agent_routes, "AgentService", UnconfiguredAgent)

    response = client.post(
        "/agent/query", json={"message": "Hello"}, headers=auth_headers
    )

    assert response.status_code == 503