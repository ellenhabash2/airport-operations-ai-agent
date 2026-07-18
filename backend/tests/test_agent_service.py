"""
Tests for the agentic loop.

A scripted stand-in replaces the Gemini client so the loop can be
tested without calling the real API.
"""

import pytest
from google.genai import types

from services.agent_service import MAX_TOOL_ITERATIONS, AgentService


def _tool_request(*calls) -> types.Content:
    """Build a model turn that requests one or more tools."""
    parts = [
        types.Part(
            function_call=types.FunctionCall(name=name, args=args)
        )
        for name, args in calls
    ]

    return types.Content(role="model", parts=parts)


def _text_answer(text: str) -> types.Content:
    """Build a model turn that answers in plain text."""
    return types.Content(role="model", parts=[types.Part.from_text(text=text)])


class ScriptedGemini:
    """Returns a predefined sequence of responses."""

    def __init__(self, script: list[types.Content]):
        self.script = script
        self.calls = 0
        self.last_contents: list[types.Content] = []
        self.tools_enabled: list[bool] = []

    def generate(self, contents, system_instruction=None, use_tools=True):
        self.last_contents = list(contents)
        self.tools_enabled.append(use_tools)
        content = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1

        return types.GenerateContentResponse(
            candidates=[types.Candidate(content=content)]
        )


def _agent_with(script: list[types.Content]) -> AgentService:
    """Build an agent backed by a scripted model."""
    agent = AgentService.__new__(AgentService)
    agent.gemini_service = ScriptedGemini(script)

    return agent


def test_empty_message_is_rejected(app):
    """An empty question never reaches the model."""
    agent = _agent_with([_text_answer("unused")])

    with pytest.raises(ValueError):
        agent.chat("   ")


def test_answer_without_tools_is_returned_directly(app):
    """A question the model answers on its own runs a single call."""
    agent = _agent_with([_text_answer("No tools needed.")])

    result = agent.chat("Hello")

    assert result["response"] == "No tools needed."
    assert result["tool_calls"] == []
    assert agent.gemini_service.calls == 1


def test_single_tool_call_is_executed(app):
    """A requested tool runs and its name is reported back."""
    agent = _agent_with(
        [
            _tool_request(("find_delayed_flights", {})),
            _text_answer("One flight is delayed."),
        ]
    )

    result = agent.chat("Which flights are delayed?")

    assert result["response"] == "One flight is delayed."
    assert [call["tool"] for call in result["tool_calls"]] == [
        "find_delayed_flights"
    ]


def test_parallel_tool_calls_are_all_executed(app):
    """Every tool requested in one turn runs, not just the first."""
    agent = _agent_with(
        [
            _tool_request(
                ("find_delayed_flights", {}),
                ("get_available_gates", {}),
                ("get_latest_weather", {}),
            ),
            _text_answer("Operational summary."),
        ]
    )

    result = agent.chat("Give me a summary")

    assert [call["tool"] for call in result["tool_calls"]] == [
        "find_delayed_flights",
        "get_available_gates",
        "get_latest_weather",
    ]


def test_chained_tool_calls_across_iterations(app):
    """
    The loop keeps running while the model asks for more tools, so a
    later tool can depend on an earlier result.
    """
    agent = _agent_with(
        [
            _tool_request(("get_flight_by_number", {"flight_number": "TA1000"})),
            _tool_request(("get_terminal_status", {})),
            _tool_request(("get_flights_by_terminal", {"terminal_id": 1.0})),
            _text_answer("Flight TA1000 departs from Terminal A."),
        ]
    )

    result = agent.chat("Where does TA1000 depart from?")

    assert len(result["tool_calls"]) == 3
    assert agent.gemini_service.calls == 4
    assert not any(call["failed"] for call in result["tool_calls"])


def test_function_results_are_sent_with_the_user_role(app):
    """Gemini only accepts the user and model roles."""
    agent = _agent_with(
        [
            _tool_request(("find_delayed_flights", {})),
            _text_answer("Done."),
        ]
    )

    agent.chat("Which flights are delayed?")

    roles = {content.role for content in agent.gemini_service.last_contents}

    assert roles == {"user", "model"}


def test_failing_tool_is_reported_and_the_loop_continues(app):
    """A bad tool name does not abort the request."""
    agent = _agent_with(
        [
            _tool_request(("does_not_exist", {})),
            _text_answer("That tool is unavailable."),
        ]
    )

    result = agent.chat("Do something impossible")

    assert result["tool_calls"][0]["failed"] is True
    assert result["response"] == "That tool is unavailable."


def test_loop_stops_at_the_iteration_limit(app):
    """
    A model that never stops requesting tools is cut off, and the final
    call is made without tools so it is forced to answer.
    """
    agent = _agent_with([_tool_request(("get_all_flights", {}))])

    result = agent.chat("Loop forever")

    assert result["truncated"] is True
    assert len(result["tool_calls"]) == MAX_TOOL_ITERATIONS
    assert agent.gemini_service.tools_enabled[-1] is False