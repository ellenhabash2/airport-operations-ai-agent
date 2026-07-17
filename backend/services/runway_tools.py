"""
AI tools for querying runways information.
"""

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