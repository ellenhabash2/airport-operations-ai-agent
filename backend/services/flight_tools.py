"""
AI tools for querying and updating flight information.
"""

from repositories.flight_repository import FlightRepository
from repositories.gate_repository import GateRepository


def get_all_flights() -> list[dict]:
    """
    Return all flights as dictionaries.
    """
    flights = FlightRepository.get_all()
    return [flight.to_dict() for flight in flights]


def get_flight_by_id(flight_id: int) -> dict:
    """
    Return a single flight by its ID.
    """
    flight = FlightRepository.get_by_id(flight_id)

    if flight is None:
        return {
            "error": f"Flight with id {flight_id} was not found."
        }

    return flight.to_dict()


def get_flight_by_number(flight_number: str) -> dict:
    """
    Return a single flight by its flight number.
    """
    flight = FlightRepository.get_by_flight_number(flight_number)

    if flight is None:
        return {
            "error": f"Flight '{flight_number}' was not found."
        }

    return flight.to_dict()


def find_delayed_flights() -> list[dict]:
    """
    Return all delayed flights.
    """
    flights = FlightRepository.get_delayed()
    return [flight.to_dict() for flight in flights]


VALID_FLIGHT_STATUSES = {
    "scheduled",
    "boarding",
    "departed",
    "arrived",
    "delayed",
    "cancelled",
}


def search_flights(
    origin: str | None = None,
    destination: str | None = None,
    status: str | None = None,
    airline_name: str | None = None,
) -> list[dict] | dict:
    """
    Search flights by any combination of route, status and airline.
    """
    if not any([origin, destination, status, airline_name]):
        return {
            "error": (
                "Provide at least one search criterion: "
                "origin, destination, status or airline_name."
            )
        }

    if status is not None:
        status = status.lower()

        if status not in VALID_FLIGHT_STATUSES:
            return {
                "error": (
                    "Invalid status. Allowed values are: "
                    f"{', '.join(sorted(VALID_FLIGHT_STATUSES))}."
                )
            }

    flights = FlightRepository.search(
        origin=origin,
        destination=destination,
        status=status,
        airline_name=airline_name,
    )

    return [flight.to_dict() for flight in flights]


def update_flight_status(flight_number: str, status: str) -> dict:
    """
    Update the operational status of a flight.
    """
    status = status.lower()

    if status not in VALID_FLIGHT_STATUSES:
        return {
            "error": (
                "Invalid status. Allowed values are: "
                f"{', '.join(sorted(VALID_FLIGHT_STATUSES))}."
            )
        }

    flight = FlightRepository.get_by_flight_number(flight_number)

    if flight is None:
        return {"error": f"Flight '{flight_number}' was not found."}

    previous_status = flight.status
    flight.status = status
    FlightRepository.save()

    return {
        "updated": True,
        "previous_status": previous_status,
        "flight": flight.to_dict(),
    }


def assign_flight_to_gate(flight_number: str, gate_number: str) -> dict:
    """
    Move a flight to another gate.

    The target gate must be free. The previous gate is released only
    when no other flight is still assigned to it.
    """
    flight = FlightRepository.get_by_flight_number(flight_number)

    if flight is None:
        return {"error": f"Flight '{flight_number}' was not found."}

    gate = GateRepository.get_by_gate_number(gate_number)

    if gate is None:
        return {"error": f"Gate '{gate_number}' was not found."}

    if gate.id == flight.gate_id:
        return {
            "error": f"Flight '{flight_number}' is already at gate '{gate_number}'."
        }

    if gate.status != "available":
        return {
            "error": (
                f"Gate '{gate_number}' is not available "
                f"(current status: {gate.status})."
            )
        }

    previous_gate = flight.gate
    flight.gate_id = gate.id
    gate.status = "occupied"

    released_gate = None

    if previous_gate is not None:
        remaining = FlightRepository.count_by_gate_id(
            previous_gate.id, exclude_flight_id=flight.id
        )

        if remaining == 0 and previous_gate.status == "occupied":
            previous_gate.status = "available"
            released_gate = previous_gate.gate_number

    FlightRepository.save()

    return {
        "updated": True,
        "flight": flight.to_dict(),
        "released_gate": released_gate,
    }