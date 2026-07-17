"""
Registry of all available AI function tools.
"""

from services.flight_tools import (
    find_delayed_flights,
    get_all_flights,
    get_flight_by_id,
    get_flight_by_number,
)
from services.gate_tools import (
    get_all_gates,
    get_available_gates,
    get_gate_by_id,
    get_gate_by_number,
)
from services.incident_tools import (
    create_incident,
    get_all_incidents,
    get_incidents_by_severity,
)
from services.runway_tools import (
    get_runway_by_code,
    get_runway_by_id,
    get_runway_status,
)
from services.terminal_tools import (
    get_flights_by_terminal,
)
from services.weather_tools import (
    get_latest_weather,
)


TOOLS = {
    # Flight tools
    "get_all_flights": get_all_flights,
    "get_flight_by_id": get_flight_by_id,
    "get_flight_by_number": get_flight_by_number,
    "find_delayed_flights": find_delayed_flights,

    # Gate tools
    "get_all_gates": get_all_gates,
    "get_gate_by_id": get_gate_by_id,
    "get_gate_by_number": get_gate_by_number,
    "get_available_gates": get_available_gates,

    # Runway tools
    "get_runway_status": get_runway_status,
    "get_runway_by_id": get_runway_by_id,
    "get_runway_by_code": get_runway_by_code,

    # Weather tools
    "get_latest_weather": get_latest_weather,

    # Incident tools
    "get_all_incidents": get_all_incidents,
    "create_incident": create_incident,
    "get_incidents_by_severity": get_incidents_by_severity,

    # Terminal tools
    "get_flights_by_terminal": get_flights_by_terminal,
}