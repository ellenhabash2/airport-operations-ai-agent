from services.presentation_service import PresentationService


def test_builds_flight_status_from_verified_tool_result():
    flight = {"id": 1, "flight_number": "SB2101", "status": "scheduled"}
    presentation = PresentationService.from_tool_calls(
        [{"tool": "get_flight_by_number", "failed": False, "result": flight}]
    )

    assert presentation == {"type": "flight_status", "data": flight}


def test_ignores_failed_or_unsupported_calls():
    assert PresentationService.from_tool_calls(
        [{"tool": "get_flight_by_number", "failed": True, "result": {}}]
    ) is None
    assert PresentationService.from_tool_calls(
        [{"tool": "get_latest_weather", "failed": False, "result": {}}]
    ) is None


def test_builds_gate_assignment_without_provider_text_parsing():
    presentation = PresentationService.from_tool_calls(
        [{
            "tool": "assign_flight_to_gate",
            "failed": False,
            "result": {
                "updated": True,
                "released_gate": "A01",
                "flight": {"flight_number": "SB2101", "gate_number": "A03", "terminal": "A"},
            },
        }]
    )

    assert presentation["type"] == "gate_assignment"
    assert presentation["data"]["new_gate"] == "A03"
