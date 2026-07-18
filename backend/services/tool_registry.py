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


TOOL_SCHEMAS = {
    "get_all_flights": {
        "description": "Return all flights in the airport database.",
        "parameters": {},
    },

    "get_flight_by_id": {
        "description": "Return a flight using its database ID.",
        "parameters": {
            "flight_id": {
                "type": "integer",
                "description": "The flight ID.",
            }
        },
        "required": [
            "flight_id",
        ],
    },

    "get_flight_by_number": {
        "description": "Return a flight using its flight number.",
        "parameters": {
            "flight_number": {
                "type": "string",
                "description": "The flight number (for example: AM2000).",
            }
        },
        "required": [
            "flight_number",
        ],
    },

    "find_delayed_flights": {
        "description": "Return all delayed flights.",
        "parameters": {},
    },

    "get_all_gates": {
        "description": "Return all airport gates.",
        "parameters": {},
    },

    "get_gate_by_id": {
        "description": "Return a gate using its database ID.",
        "parameters": {
            "gate_id": {
                "type": "integer",
                "description": "The gate ID.",
            }
        },
        "required": [
            "gate_id",
        ],
    },

    "get_gate_by_number": {
        "description": "Return a gate using its gate number.",
        "parameters": {
            "gate_number": {
                "type": "string",
                "description": "The gate number (for example: A01 or B12).",
            }
        },
        "required": [
            "gate_number",
        ],
    },

    "get_available_gates": {
        "description": "Return all currently available gates.",
        "parameters": {},
    },

    "get_all_incidents": {
        "description": "Return all airport incidents.",
        "parameters": {},
    },

    "get_incidents_by_severity": {
        "description": "Return all incidents with a specific severity level.",
        "parameters": {
            "severity": {
                "type": "string",
                "enum": [
                    "low",
                    "medium",
                    "high",
                    "critical",
                ],
            }
        },
        "required": [
            "severity",
        ],
    },

    "create_incident": {
        "description": "Create a new airport incident.",
        "parameters": {
            "title": {
                "type": "string",
            },
            "description": {
                "type": "string",
            },
            "severity": {
                "type": "string",
                "enum": [
                    "low",
                    "medium",
                    "high",
                    "critical",
                ],
            },
            "location": {
                "type": "string",
            },
        },
        "required": [
            "title",
            "description",
            "severity",
            "location",
        ],
    },

    "get_runway_by_id": {
        "description": "Return a runway using its database ID.",
        "parameters": {
            "runway_id": {
                "type": "integer",
                "description": "The runway ID.",
            }
        },
        "required": [
            "runway_id",
        ],
    },

    "get_runway_by_code": {
        "description": "Return a runway using its runway code.",
        "parameters": {
            "runway_code": {
                "type": "string",
                "description": "The runway code (for example: 08L/26R).",
            }
        },
        "required": [
            "runway_code",
        ],
    },

    "get_runway_status": {
        "description": "Return the status of all airport runways.",
        "parameters": {},
    },

    "get_flights_by_terminal": {
        "description": "Return all flights assigned to a terminal.",
        "parameters": {
            "terminal_id": {
                "type": "integer",
                "description": "The terminal ID.",
            }
        },
        "required": [
            "terminal_id",
        ],
    },

    "get_latest_weather": {
        "description": "Return the latest airport weather report.",
        "parameters": {},
    },
}