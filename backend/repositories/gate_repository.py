"""
Database access layer for Gate entities.
"""

from database import db
from models.gate import Gate


class GateRepository:
    """Repository for gate database operations."""

    @staticmethod
    def get_all() -> list[Gate]:
        """Return all gates."""
        return Gate.query.all()

    @staticmethod
    def get_by_id(gate_id: int) -> Gate | None:
        """Return a gate by its ID."""
        return db.session.get(Gate, gate_id)

    @staticmethod
    def get_by_gate_number(gate_number: str) -> Gate | None:
        """Return a gate by its gate number."""
        return Gate.query.filter_by(gate_number=gate_number).first()

    @staticmethod
    def get_available() -> list[Gate]:
        """Return all available gates."""
        return Gate.query.filter_by(status="available").all()