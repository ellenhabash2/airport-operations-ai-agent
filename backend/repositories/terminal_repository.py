"""
Database access layer for Terminal entities.
"""

from database import db
from models.flight import Flight
from models.terminal import Terminal
from repositories.flight_repository import FlightRepository


class TerminalRepository:
    """Repository for terminal database operations."""

    @staticmethod
    def get_all() -> list[Terminal]:
        """
        Return all terminals ordered by name.
        """
        return Terminal.query.order_by(Terminal.name.asc()).all()

    @staticmethod
    def get_by_id(terminal_id: int) -> Terminal | None:
        """
        Return a terminal by its ID.
        """
        return db.session.get(Terminal, terminal_id)

    @staticmethod
    def get_flights(terminal_id: int) -> list[Flight]:
        """
        Return all flights assigned to the given terminal.
        """
        return FlightRepository.get_by_terminal_id(terminal_id)