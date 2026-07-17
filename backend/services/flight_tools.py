"""
AI tools for querying flight information.
"""

from repositories.flight_repository import FlightRepository


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