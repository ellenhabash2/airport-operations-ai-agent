"""Build trusted UI presentation metadata from executed tool results."""


class PresentationService:
    """Maps known operational tool results to stable presentation contracts."""

    FLIGHT_LIST_TOOLS = {
        "get_all_flights",
        "find_delayed_flights",
        "search_flights",
        "get_flights_by_terminal",
    }

    @classmethod
    def from_tool_calls(cls, tool_calls: list[dict] | None) -> dict | None:
        successful = [call for call in (tool_calls or []) if not call.get("failed")]
        if not successful:
            return None

        call = successful[-1]
        tool = call.get("tool")
        result = call.get("result")

        if tool in {"get_flight_by_id", "get_flight_by_number"} and isinstance(result, dict):
            return {"type": "flight_status", "data": result}

        if tool in cls.FLIGHT_LIST_TOOLS and isinstance(result, list):
            return {"type": "flight_list", "data": {"flights": result}}

        if tool == "assign_flight_to_gate" and isinstance(result, dict):
            flight = result.get("flight") or {}
            return {
                "type": "gate_assignment",
                "data": {
                    "flight_number": flight.get("flight_number"),
                    "previous_gate": result.get("released_gate"),
                    "new_gate": flight.get("gate_number"),
                    "terminal": flight.get("terminal"),
                    "status": "success" if result.get("updated") else "failed",
                },
            }

        if tool in {"get_runway_by_id", "get_runway_by_code"} and isinstance(result, dict):
            return {"type": "runway_status", "data": result}

        if tool == "get_runway_status" and isinstance(result, list):
            return {"type": "runway_status", "data": {"runways": result}}

        if tool == "update_runway_status" and isinstance(result, dict):
            runway = dict(result.get("runway") or {})
            runway["affected_flights"] = result.get("affected_flights") or []
            return {"type": "runway_status", "data": runway}

        return None
