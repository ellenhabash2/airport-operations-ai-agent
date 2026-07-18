"""
Tests for the tools that search and modify airport data.
"""

from services.tool_executor import ToolExecutor


def test_search_requires_at_least_one_criterion(app):
    """An unfiltered search is refused rather than returning everything."""
    result = ToolExecutor.execute("search_flights", {})

    assert "error" in result


def test_search_by_status(app):
    """Flights can be filtered by operational status."""
    result = ToolExecutor.execute("search_flights", {"status": "delayed"})

    assert [flight["flight_number"] for flight in result] == ["TA1000"]


def test_search_by_partial_airline_name(app):
    """Airline names are matched partially and case-insensitively."""
    result = ToolExecutor.execute("search_flights", {"airline_name": "test"})

    assert len(result) == 2


def test_search_combines_criteria(app):
    """Several criteria narrow the result set together."""
    result = ToolExecutor.execute(
        "search_flights", {"destination": "CDG", "status": "delayed"}
    )

    assert len(result) == 1


def test_search_with_invalid_status_is_rejected(app):
    """An unknown status is reported instead of returning nothing."""
    result = ToolExecutor.execute("search_flights", {"status": "landed"})

    assert "error" in result


def test_update_flight_status(app):
    """A flight status change is persisted and the old value reported."""
    result = ToolExecutor.execute(
        "update_flight_status",
        {"flight_number": "TA1000", "status": "cancelled"},
    )
    reloaded = ToolExecutor.execute(
        "get_flight_by_number", {"flight_number": "TA1000"}
    )

    assert result["previous_status"] == "delayed"
    assert reloaded["status"] == "cancelled"


def test_update_flight_status_rejects_unknown_status(app):
    """Only the allowed status values are accepted."""
    result = ToolExecutor.execute(
        "update_flight_status",
        {"flight_number": "TA1000", "status": "exploded"},
    )

    assert "error" in result


def test_update_unknown_flight_is_reported(app):
    """Updating a flight that does not exist returns an error."""
    result = ToolExecutor.execute(
        "update_flight_status",
        {"flight_number": "ZZ9999", "status": "delayed"},
    )

    assert "error" in result


def test_assign_flight_to_gate_releases_the_previous_gate(app):
    """
    Moving the only flight off a gate frees that gate for reuse.
    """
    result = ToolExecutor.execute(
        "assign_flight_to_gate",
        {"flight_number": "TA1001", "gate_number": "A02"},
    )
    gates = {
        gate["gate_number"]: gate
        for gate in ToolExecutor.execute("get_all_gates")
    }

    assert result["released_gate"] == "B01"
    assert result["flight"]["gate_number"] == "A02"
    assert gates["A02"]["status"] == "occupied"
    assert gates["B01"]["status"] == "available"


def test_assign_flight_to_an_occupied_gate_is_refused(app):
    """A gate that is not available cannot receive another flight."""
    result = ToolExecutor.execute(
        "assign_flight_to_gate",
        {"flight_number": "TA1000", "gate_number": "B01"},
    )

    assert "error" in result


def test_assign_flight_to_its_current_gate_is_refused(app):
    """Reassigning a flight to the gate it already uses is rejected."""
    result = ToolExecutor.execute(
        "assign_flight_to_gate",
        {"flight_number": "TA1000", "gate_number": "A01"},
    )

    assert "error" in result


def test_update_runway_status_reports_affected_flights(app):
    """Closing a runway lists the flights assigned to it."""
    result = ToolExecutor.execute(
        "update_runway_status",
        {"runway_code": "08L/26R", "status": "closed"},
    )

    assert result["previous_status"] == "available"
    assert result["runway"]["status"] == "closed"
    assert result["affected_flight_count"] == 2


def test_update_runway_status_rejects_unknown_status(app):
    """Only the allowed runway statuses are accepted."""
    result = ToolExecutor.execute(
        "update_runway_status",
        {"runway_code": "08L/26R", "status": "flooded"},
    )

    assert "error" in result


def test_search_incidents_matches_any_text_field(app):
    """Free text search looks at the title, description and location."""
    by_title = ToolExecutor.execute("search_incidents", {"keyword": "inspection"})
    by_location = ToolExecutor.execute("search_incidents", {"keyword": "A01"})

    assert len(by_title) == 1
    assert len(by_location) == 1


def test_search_incidents_requires_a_keyword(app):
    """An empty keyword is refused."""
    result = ToolExecutor.execute("search_incidents", {"keyword": "   "})

    assert "error" in result


def test_search_incidents_with_no_match_returns_empty(app):
    """A search with no results is an empty list, not an error."""
    result = ToolExecutor.execute("search_incidents", {"keyword": "volcano"})

    assert result == []