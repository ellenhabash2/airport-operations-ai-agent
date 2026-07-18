"""
Database access layer for Flight entities.
"""

from database import db
from models.airline import Airline
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

    @staticmethod
    def get_by_runway_id(runway_id: int) -> list[Flight]:
        """Return all flights assigned to the given runway."""
        return Flight.query.filter_by(runway_id=runway_id).all()

    @staticmethod
    def count_by_gate_id(gate_id: int, exclude_flight_id: int) -> int:
        """
        Count the flights still assigned to a gate, ignoring one flight.
        """
        return (
            Flight.query
            .filter(Flight.gate_id == gate_id)
            .filter(Flight.id != exclude_flight_id)
            .count()
        )

    @staticmethod
    def search(
        origin: str | None = None,
        destination: str | None = None,
        status: str | None = None,
        airline_name: str | None = None,
    ) -> list[Flight]:
        """
        Return flights matching every criterion that was provided.

        Text criteria are matched case-insensitively and partially, so
        "sky" matches "SkyBridge Airways".
        """
        query = Flight.query

        if origin:
            query = query.filter(Flight.origin.ilike(f"%{origin}%"))

        if destination:
            query = query.filter(Flight.destination.ilike(f"%{destination}%"))

        if status:
            query = query.filter(Flight.status == status)

        if airline_name:
            query = (
                query
                .join(Airline)
                .filter(Airline.name.ilike(f"%{airline_name}%"))
            )

        return query.order_by(Flight.departure_time.asc()).all()

    @staticmethod
    def save() -> None:
        """Persist pending changes."""
        db.session.commit()