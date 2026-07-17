"""
Database access layer for Flight entities.
"""

from database import db
from models.flight import Flight


class FlightRepository:
    """Repository for flight database operations."""

    @staticmethod
    def get_all() -> list[Flight]:
        """Return all flights."""
        return Flight.query.all()

    @staticmethod
    def get_by_id(flight_id: int) -> Flight | None:
        """Return a flight by its ID."""
        return db.session.get(Flight, flight_id)

    @staticmethod
    def get_by_flight_number(flight_number: str) -> Flight | None:
        """Return a flight by its flight number."""
        return Flight.query.filter_by(flight_number=flight_number).first()

    @staticmethod
    def get_delayed() -> list[Flight]:
        """Return all delayed flights."""
        return Flight.query.filter_by(status="delayed").all()