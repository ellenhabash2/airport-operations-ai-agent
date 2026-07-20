"""
Database access layer for Gate entities.
"""

from sqlalchemy.orm import joinedload

from database import db
from models.gate import Gate


class GateRepository:
    """Repository for gate database operations."""

    @staticmethod
    def _query():
        """
        Return a gate query that eagerly loads the terminal.

        `Gate.to_dict()` reads the terminal name, so listing gates without
        eager loading issues one extra query per terminal.
        """
        return Gate.query.options(joinedload(Gate.terminal))

    @staticmethod
    def get_all() -> list[Gate]:
        """Return all gates ordered by gate number."""
        return GateRepository._query().order_by(Gate.gate_number.asc()).all()

    @staticmethod
    def get_by_id(gate_id: int) -> Gate | None:
        """Return a gate by its ID."""
        return db.session.get(Gate, gate_id)

    @staticmethod
    def get_by_gate_number(gate_number: str) -> Gate | None:
        """Return a gate by its gate number."""
        return (
            GateRepository._query()
            .filter(Gate.gate_number == gate_number)
            .first()
        )

    @staticmethod
    def get_available() -> list[Gate]:
        """Return all available gates."""
        return (
            GateRepository._query()
            .filter(Gate.status == "available")
            .order_by(Gate.gate_number.asc())
            .all()
        )

    @staticmethod
    def save() -> None:
        """Persist pending changes."""
        db.session.commit()