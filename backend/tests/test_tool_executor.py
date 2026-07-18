"""
Tests for the tool execution layer.
"""

from services.tool_executor import ToolExecutor


def test_known_tool_returns_data(app):
    """A registered tool returns its result."""
    result = ToolExecutor.execute("find_delayed_flights")

    assert len(result) == 1
    assert result[0]["flight_number"] == "TA1000"


def test_unknown_tool_returns_error_instead_of_raising(app):
    """An unknown tool name is reported as data, not an exception."""
    result = ToolExecutor.execute("no_such_tool", {})

    assert "error" in result
    assert "no_such_tool" in result["error"]


def test_invalid_argument_name_returns_error(app):
    """Wrong argument names are reported instead of crashing the request."""
    result = ToolExecutor.execute("get_flight_by_id", {"wrong_name": 1})

    assert "error" in result


def test_float_id_is_coerced_to_integer(app):
    """
    Gemini sends every number as a float, so integer arguments must be cast.
    """
    result = ToolExecutor.execute("get_flight_by_id", {"flight_id": 1.0})

    assert result["flight_number"] == "TA1000"


def test_missing_record_returns_error_payload(app):
    """A lookup that finds nothing returns a readable error."""
    result = ToolExecutor.execute("get_flight_by_id", {"flight_id": 999})

    assert "error" in result


def test_invalid_severity_is_rejected(app):
    """Tool level validation rejects values outside the allowed set."""
    result = ToolExecutor.execute(
        "create_incident",
        {
            "title": "Test",
            "description": "Test incident.",
            "severity": "catastrophic",
            "location": "Gate A01",
        },
    )

    assert "error" in result


def test_create_incident_writes_to_the_database(app):
    """The write tool persists a new incident."""
    before = ToolExecutor.execute("get_all_incidents")

    created = ToolExecutor.execute(
        "create_incident",
        {
            "title": "Bird strike",
            "description": "Reported on approach.",
            "severity": "high",
            "location": "Runway 08L/26R",
        },
    )

    after = ToolExecutor.execute("get_all_incidents")

    assert created["title"] == "Bird strike"
    assert len(after) == len(before) + 1


def test_terminal_status_reports_gate_availability(app):
    """The terminal overview counts free gates per terminal."""
    result = ToolExecutor.execute("get_terminal_status")
    terminals = {entry["name"]: entry for entry in result}

    assert terminals["Terminal A"]["available_gates"] == 1
    assert terminals["Terminal B"]["available_gates"] == 0