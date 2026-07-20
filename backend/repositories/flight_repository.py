"""
Database access layer for Flight entities.
"""

from sqlalchemy.orm import joinedload

from database import db
from models.airline import Airline
from models.flight import Flight
from models.gate import Gate


class FlightRepository:
    """Repository for flight database operations."""

    @staticmethod
    def _query():
        """
        Return a flight query that eagerly loads every related row.

        `Flight.to_dict()` reads the airline, aircraft, gate, terminal and
        runway of each flight. Without eager loading, listing flights issues
        one extra query per distinct related row.
        """
        return Flight.query.options(
            joinedload(Flight.airline),
            joinedload(Flight.aircraft),
            joinedload(Flight.gate).joinedload(Gate.terminal),
            joinedload(Flight.runway),
        )

    @staticmethod
    def get_all() -> list[Flight]:
        """Return all flights, earliest departure first."""
        return (
            FlightRepository._query()
            .order_by(Flight.departure_time.asc())
            .all()
        )

    @staticmethod
    def get_by_id(flight_id: int) -> Flight | None:
        """Return a flight by its ID."""
        return db.session.get(Flight, flight_id)

    @staticmethod
    def get_by_flight_number(flight_number: str) -> Flight | None:
        """Return a flight by its flight number."""
        return (
            FlightRepository._query()
            .filter(Flight.flight_number == flight_number)
            .first()
        )

    @staticmethod
    def get_delayed() -> list[Flight]:
        """Return all delayed flights."""
        return (
            FlightRepository._query()
            .filter(Flight.status == "delayed")
            .order_by(Flight.departure_time.asc())
            .all()
        )

    @staticmethod
    def get_by_runway_id(runway_id: int) -> list[Flight]:
        """Return all flights assigned to the given runway."""
        return (
            FlightRepository._query()
            .filter(Flight.runway_id == runway_id)
            .all()
        )

    @staticmethod
    def get_by_terminal_id(terminal_id: int) -> list[Flight]:
        """Return all flights whose gate belongs to the given terminal."""
        return (
            FlightRepository._query()
            .join(Gate, Flight.gate_id == Gate.id)
            .filter(Gate.terminal_id == terminal_id)
            .order_by(Flight.departure_time.asc())
            .all()
        )

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
        query = FlightRepository._query()

        if origin:
            query = query.filter(Flight.origin.ilike(f"%{origin}%"))

        if destination:
            query = query.filter(Flight.destination.ilike(f"%{destination}%"))

        if status:
            query = query.filter(Flight.status == status)

        if airline_name:
            query = (
                query
                .join(Airline, Flight.airline_id == Airline.id)
                .filter(Airline.name.ilike(f"%{airline_name}%"))
            )

        return query.order_by(Flight.departure_time.asc()).all()

    @staticmethod
    def save() -> None:
        """Persist pending changes."""
        db.session.commit()