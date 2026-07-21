"""
Tests for conversation memory.
"""

from google.genai import types

import routes.agent_routes as agent_routes
from models.conversation import Conversation
from models.message import Message
from repositories.conversation_repository import ConversationRepository
from services.memory_service import HISTORY_LIMIT, MemoryService


class RecordingAgent:
    """Records the history it was given and returns a fixed answer."""

    seen_history: list = []

    def __init__(self):
        pass

    def chat(self, message, history=None):
        RecordingAgent.seen_history = list(history or [])
        turns = list(history or [])
        turns.append(
            types.Content(
                role="user", parts=[types.Part.from_text(text=message)]
            )
        )
        turns.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=f"answer to: {message}")],
            )
        )

        return {
            "response": f"answer to: {message}",
            "tool_calls": [],
            "history": turns,
        }


class ToolRecordingAgent(RecordingAgent):
    """Returns configurable tool metadata with a readable answer."""

    tool_calls: list[dict] = []

    def chat(self, message, history=None):
        result = super().chat(message, history=history)
        result["tool_calls"] = list(self.tool_calls)
        return result


def _ask(client, headers, message, conversation_id=None):
    """Send a question to the agent endpoint."""
    payload = {"message": message}

    if conversation_id is not None:
        payload["conversation_id"] = conversation_id

    return client.post("/agent/query", json=payload, headers=headers)


def test_title_is_derived_from_the_first_message(app):
    """A conversation is named after the question that started it."""
    assert MemoryService.build_title("  Which  gates are free? ") == (
        "Which gates are free?"
    )
    assert MemoryService.build_title("x" * 200).endswith("...")
    assert MemoryService.build_title("   ") == "New conversation"


def test_tool_calls_survive_a_round_trip(app):
    """A stored tool call is replayed exactly as Gemini produced it."""
    conversation = ConversationRepository.create(user_id=1, title="Test")
    original = types.Content(
        role="model",
        parts=[
            types.Part(
                function_call=types.FunctionCall(
                    name="get_flight_by_id", args={"flight_id": 7}
                )
            )
        ],
    )

    MemoryService.record_turns(conversation, [original])
    restored = MemoryService.load_history(conversation)

    assert len(restored) == 1
    assert restored[0].parts[0].function_call.name == "get_flight_by_id"
    assert restored[0].parts[0].function_call.args == {"flight_id": 7}


def test_history_is_capped(app):
    """Only the most recent turns are replayed."""
    conversation = ConversationRepository.create(user_id=1, title="Test")
    turns = [
        types.Content(
            role="user", parts=[types.Part.from_text(text=f"message {i}")]
        )
        for i in range(HISTORY_LIMIT + 10)
    ]

    MemoryService.record_turns(conversation, turns)
    restored = MemoryService.load_history(conversation)

    assert len(restored) == HISTORY_LIMIT
    assert restored[-1].parts[0].text == f"message {HISTORY_LIMIT + 9}"


def test_a_corrupt_row_is_skipped(app):
    """One unreadable row does not break the conversation."""
    conversation = ConversationRepository.create(user_id=1, title="Test")
    MemoryService.record_turns(
        conversation,
        [types.Content(role="user", parts=[types.Part.from_text(text="ok")])],
    )
    conversation.messages[0].payload = "not json"

    good = types.Content(
        role="model", parts=[types.Part.from_text(text="fine")]
    )
    MemoryService.record_turns(conversation, [good])

    restored = MemoryService.load_history(conversation)

    assert len(restored) == 1
    assert restored[0].parts[0].text == "fine"


def test_a_first_question_opens_a_conversation(client, auth_headers, monkeypatch):
    """Asking without an id starts a thread and returns its id."""
    monkeypatch.setattr(agent_routes, "AgentService", RecordingAgent)

    response = _ask(client, auth_headers, "Which gates are free?")
    data = response.get_json()["data"]

    assert response.status_code == 200
    assert isinstance(data["conversation_id"], int)


def test_a_follow_up_receives_the_earlier_turns(
    client, auth_headers, monkeypatch
):
    """The second question is sent to the model with the first exchange."""
    monkeypatch.setattr(agent_routes, "AgentService", RecordingAgent)

    first = _ask(client, auth_headers, "Which flights are delayed?")
    conversation_id = first.get_json()["data"]["conversation_id"]

    _ask(client, auth_headers, "And which of those are at Terminal B?",
         conversation_id=conversation_id)

    replayed = [
        part.text
        for content in RecordingAgent.seen_history
        for part in content.parts
    ]

    assert "Which flights are delayed?" in replayed
    assert "answer to: Which flights are delayed?" in replayed


def test_a_new_conversation_starts_empty(client, auth_headers, monkeypatch):
    """Leaving the id out starts a fresh thread with no history."""
    monkeypatch.setattr(agent_routes, "AgentService", RecordingAgent)

    _ask(client, auth_headers, "First thread")
    _ask(client, auth_headers, "Second thread")

    assert RecordingAgent.seen_history == []


def test_an_unknown_conversation_is_rejected(client, auth_headers, monkeypatch):
    """Continuing a thread that does not exist returns 404."""
    monkeypatch.setattr(agent_routes, "AgentService", RecordingAgent)

    response = _ask(client, auth_headers, "Hello", conversation_id=999)

    assert response.status_code == 404


def test_another_users_conversation_is_not_reachable(
    app, client, auth_headers, monkeypatch
):
    """A conversation belonging to someone else is invisible."""
    monkeypatch.setattr(agent_routes, "AgentService", RecordingAgent)
    other = ConversationRepository.create(user_id=999, title="Not yours")

    asked = _ask(client, auth_headers, "Hello", conversation_id=other.id)
    fetched = client.get(
        f"/agent/conversations/{other.id}", headers=auth_headers
    )

    assert asked.status_code == 404
    assert fetched.status_code == 404


def test_conversations_are_listed(client, auth_headers, monkeypatch):
    """The list endpoint returns the user's own threads."""
    monkeypatch.setattr(agent_routes, "AgentService", RecordingAgent)
    _ask(client, auth_headers, "Which gates are free?")

    response = client.get("/agent/conversations", headers=auth_headers)
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["data"][0]["title"] == "Which gates are free?"


def test_a_conversation_returns_its_messages(
    client, auth_headers, monkeypatch
):
    """Fetching a thread returns the readable turns in order."""
    monkeypatch.setattr(agent_routes, "AgentService", RecordingAgent)
    conversation_id = (
        _ask(client, auth_headers, "Hello").get_json()["data"]["conversation_id"]
    )

    response = client.get(
        f"/agent/conversations/{conversation_id}", headers=auth_headers
    )
    messages = response.get_json()["data"]["messages"]

    assert response.status_code == 200
    assert [message["role"] for message in messages] == ["user", "model"]
    assert messages[0]["text"] == "Hello"


def test_assistant_tool_calls_are_persisted_after_a_query(
    app, client, auth_headers, monkeypatch
):
    """The metadata returned by the agent is stored on its answer."""
    monkeypatch.setattr(agent_routes, "AgentService", ToolRecordingAgent)
    ToolRecordingAgent.tool_calls = [
        {
            "tool": "get_available_gates",
            "arguments": {"terminal_id": 1},
            "failed": False,
        }
    ]

    conversation_id = (
        _ask(client, auth_headers, "Which gates are free?")
        .get_json()["data"]["conversation_id"]
    )
    assistant = ConversationRepository.get_messages(conversation_id)[-1]

    assert assistant.role == "model"
    assert assistant.tool_calls == ToolRecordingAgent.tool_calls


def test_retrieved_tool_calls_preserve_order(
    client, auth_headers, monkeypatch
):
    """History returns every stored call in execution order."""
    monkeypatch.setattr(agent_routes, "AgentService", ToolRecordingAgent)
    ToolRecordingAgent.tool_calls = [
        {"tool": "first_tool", "arguments": {}, "failed": False},
        {"tool": "second_tool", "arguments": {}, "failed": False},
        {"tool": "third_tool", "arguments": {}, "failed": False},
    ]
    conversation_id = (
        _ask(client, auth_headers, "Give me a summary")
        .get_json()["data"]["conversation_id"]
    )

    response = client.get(
        f"/agent/conversations/{conversation_id}", headers=auth_headers
    )
    assistant = response.get_json()["data"]["messages"][-1]

    assert [call["tool"] for call in assistant["tool_calls"]] == [
        "first_tool",
        "second_tool",
        "third_tool",
    ]


def test_failed_tool_calls_and_errors_are_persisted(
    app, client, auth_headers, monkeypatch
):
    """Failed executions retain both their state and error detail."""
    monkeypatch.setattr(agent_routes, "AgentService", ToolRecordingAgent)
    ToolRecordingAgent.tool_calls = [
        {
            "tool": "does_not_exist",
            "arguments": {"flight_id": 7},
            "failed": True,
            "error": "Unknown tool: does_not_exist",
        }
    ]

    conversation_id = (
        _ask(client, auth_headers, "Run it")
        .get_json()["data"]["conversation_id"]
    )
    stored = ConversationRepository.get_messages(conversation_id)[-1]

    assert stored.tool_calls[0]["failed"] is True
    assert stored.tool_calls[0]["error"] == "Unknown tool: does_not_exist"


def test_messages_without_tool_calls_return_an_empty_list(
    client, auth_headers, monkeypatch
):
    """Ordinary messages keep the stable array-shaped API contract."""
    monkeypatch.setattr(agent_routes, "AgentService", RecordingAgent)
    conversation_id = (
        _ask(client, auth_headers, "Hello")
        .get_json()["data"]["conversation_id"]
    )

    response = client.get(
        f"/agent/conversations/{conversation_id}", headers=auth_headers
    )

    assert all(
        message["tool_calls"] == []
        for message in response.get_json()["data"]["messages"]
    )


def test_legacy_null_tool_calls_return_an_empty_list(app):
    """Messages created before the migration remain serializable."""
    conversation = ConversationRepository.create(user_id=1, title="Legacy")
    message = Message(
        role="model",
        text="Older answer",
        payload='{"role":"model","parts":[{"text":"Older answer"}]}',
        tool_calls=None,
    )
    ConversationRepository.add_messages(conversation, [message])

    assert message.to_dict()["tool_calls"] == []


def test_another_users_persisted_tool_calls_are_not_retrievable(
    app, client, auth_headers
):
    """Ownership checks protect tool metadata with the rest of the thread."""
    other = ConversationRepository.create(user_id=999, title="Private")
    ConversationRepository.add_messages(
        other,
        [
            Message(
                role="model",
                text="Private answer",
                payload=(
                    '{"role":"model","parts":'
                    '[{"text":"Private answer"}]}'
                ),
                tool_calls=[
                    {"tool": "private_tool", "arguments": {}, "failed": False}
                ],
            )
        ],
    )

    response = client.get(
        f"/agent/conversations/{other.id}", headers=auth_headers
    )

    assert response.status_code == 404


def test_a_conversation_can_be_deleted(app, client, auth_headers, monkeypatch):
    """Deleting a thread removes it and its messages."""
    monkeypatch.setattr(agent_routes, "AgentService", RecordingAgent)
    conversation_id = (
        _ask(client, auth_headers, "Hello").get_json()["data"]["conversation_id"]
    )

    response = client.delete(
        f"/agent/conversations/{conversation_id}", headers=auth_headers
    )

    assert response.status_code == 200
    assert Conversation.query.count() == 0


def test_conversation_endpoints_require_a_token(client):
    """The conversation endpoints are not reachable anonymously."""
    assert client.get("/agent/conversations").status_code == 401
    assert client.get("/agent/conversations/1").status_code == 401
    assert client.delete("/agent/conversations/1").status_code == 401
