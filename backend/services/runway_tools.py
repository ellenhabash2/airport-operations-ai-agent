"""
AI tools for querying and updating runway information.
"""

from repositories.flight_repository import FlightRepository
from repositories.runway_repository import RunwayRepository

def get_runway_by_id(runway_id: int) -> dict:
    """
    Return a runway by its ID.
    """
    runway = RunwayRepository.get_by_id(runway_id)

    if runway is None:
        return {
            "error": f"Runway with id {runway_id} was not found."
        }

    return runway.to_dict()


def get_runway_by_code(runway_code: str) -> dict:
    """
    Return a runway by its runway code.
    """
    runway = RunwayRepository.get_by_runway_code(runway_code)

    if runway is None:
        return {
            "error": f"Runway '{runway_code}' was not found."
        }

    return runway.to_dict()


def get_runway_status() -> list[dict]:
    """
    Return the status of all runways.
    """
    runways = RunwayRepository.get_all()
    return [runway.to_dict() for runway in runways]

VALID_RUNWAY_STATUSES = {
    "available",
    "maintenance",
    "closed",
}

def update_runway_status(runway_code: str, status: str) -> dict:
    """
    Change a runway's status and report the flights it affects.
    """
    status = status.lower()

    if status not in VALID_RUNWAY_STATUSES:
        return {
            "error": (
                "Invalid status. Allowed values are: "
                f"{', '.join(sorted(VALID_RUNWAY_STATUSES))}."
            )
        }

    runway = RunwayRepository.get_by_runway_code(runway_code)

    if runway is None:
        return {"error": f"Runway '{runway_code}' was not found."}

    previous_status = runway.status
    runway.status = status
    RunwayRepository.save()

    affected = FlightRepository.get_by_runway_id(runway.id)

    return {
        "updated": True,
        "previous_status": previous_status,
        "runway": runway.to_dict(),
        "affected_flight_count": len(affected),
        "affected_flights": [
            {
                "flight_number": flight.flight_number,
                "status": flight.status,
                "origin": flight.origin,
                "destination": flight.destination,
            }
            for flight in affected
        ],
    }