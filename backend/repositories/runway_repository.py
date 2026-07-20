"""
Database access layer for Runway entities.
"""

from database import db
from models.runway import Runway


class RunwayRepository:
    """Repository for runway database operations."""

    @staticmethod
    def get_all() -> list[Runway]:
        """Return all runways."""
        return Runway.query.order_by(Runway.runway_code.asc()).all()

    @staticmethod
    def get_by_id(runway_id: int) -> Runway | None:
        """Return a runway by its ID."""
        return db.session.get(Runway, runway_id)

    @staticmethod
    def get_by_runway_code(runway_code: str) -> Runway | None:
        """Return a runway by its runway code."""
        return Runway.query.filter_by(runway_code=runway_code).first()

    @staticmethod
    def save() -> None:
        """Persist pending changes."""
        db.session.commit()