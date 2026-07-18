"""
Registry of all available AI function tools.
"""

from services.flight_tools import (
    assign_flight_to_gate,
    find_delayed_flights,
    get_all_flights,
    get_flight_by_id,
    get_flight_by_number,
    search_flights,
    update_flight_status,
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
    search_incidents,
)
from services.runway_tools import (
    get_runway_by_code,
    get_runway_by_id,
    get_runway_status,
    update_runway_status,
)
from services.terminal_tools import (
    get_flights_by_terminal,
    get_terminal_status,
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
    "search_flights": search_flights,
    "update_flight_status": update_flight_status,
    "assign_flight_to_gate": assign_flight_to_gate,

    # Gate tools
    "get_all_gates": get_all_gates,
    "get_gate_by_id": get_gate_by_id,
    "get_gate_by_number": get_gate_by_number,
    "get_available_gates": get_available_gates,

    # Runway tools
    "get_runway_status": get_runway_status,
    "get_runway_by_id": get_runway_by_id,
    "get_runway_by_code": get_runway_by_code,
    "update_runway_status": update_runway_status,

    # Weather tools
    "get_latest_weather": get_latest_weather,

    # Incident tools
    "get_all_incidents": get_all_incidents,
    "create_incident": create_incident,
    "get_incidents_by_severity": get_incidents_by_severity,
    "search_incidents": search_incidents,

    # Terminal tools
    "get_flights_by_terminal": get_flights_by_terminal,
    "get_terminal_status": get_terminal_status,
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

    "search_flights": {
        "description": (
            "Search flights by any combination of origin, destination, "
            "status and airline name. Text is matched partially and is "
            "not case sensitive. At least one criterion is required."
        ),
        "parameters": {
            "origin": {
                "type": "string",
                "description": "Departure airport, for example TLV.",
            },
            "destination": {
                "type": "string",
                "description": "Arrival airport, for example LHR.",
            },
            "status": {
                "type": "string",
                "enum": [
                    "scheduled",
                    "boarding",
                    "departed",
                    "arrived",
                    "delayed",
                    "cancelled",
                ],
            },
            "airline_name": {
                "type": "string",
                "description": "Full or partial airline name.",
            },
        },
    },

    "update_flight_status": {
        "description": "Change the operational status of a flight.",
        "parameters": {
            "flight_number": {
                "type": "string",
                "description": "The flight number, for example AM2000.",
            },
            "status": {
                "type": "string",
                "enum": [
                    "scheduled",
                    "boarding",
                    "departed",
                    "arrived",
                    "delayed",
                    "cancelled",
                ],
            },
        },
        "required": [
            "flight_number",
            "status",
        ],
    },

    "assign_flight_to_gate": {
        "description": (
            "Move a flight to a different gate. The target gate must be "
            "available. The previous gate is released when no other "
            "flight is assigned to it."
        ),
        "parameters": {
            "flight_number": {
                "type": "string",
                "description": "The flight number, for example AM2000.",
            },
            "gate_number": {
                "type": "string",
                "description": "The target gate number, for example B07.",
            },
        },
        "required": [
            "flight_number",
            "gate_number",
        ],
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

    "search_incidents": {
        "description": (
            "Search incidents by free text across the title, description "
            "and location fields."
        ),
        "parameters": {
            "keyword": {
                "type": "string",
                "description": "Text to look for, for example 'bird'.",
            }
        },
        "required": [
            "keyword",
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

    "update_runway_status": {
        "description": (
            "Change a runway's status and report which flights are "
            "assigned to it. Use this when opening or closing a runway."
        ),
        "parameters": {
            "runway_code": {
                "type": "string",
                "description": "The runway code, for example 08L/26R.",
            },
            "status": {
                "type": "string",
                "enum": [
                    "available",
                    "maintenance",
                    "closed",
                ],
            },
        },
        "required": [
            "runway_code",
            "status",
        ],
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

    "get_terminal_status": {
        "description": (
            "Return every terminal with its capacity and gate availability."
        ),
        "parameters": {},
    },

    "get_latest_weather": {
        "description": "Return the latest airport weather report.",
        "parameters": {},
    },
}