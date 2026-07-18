"""
Database access layer for Incident entities.
"""

from database import db
from models.incident import Incident


class IncidentRepository:
    """Repository for incident database operations."""

    @staticmethod
    def get_all() -> list[Incident]:
        """
        Return all incidents ordered from newest to oldest.
        """
        return (
            Incident.query
            .order_by(Incident.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_severity(severity: str) -> list[Incident]:
        """
        Return all incidents with the given severity.
        """
        return (
            Incident.query
            .filter_by(severity=severity)
            .order_by(Incident.created_at.desc())
            .all()
        )

    @staticmethod
    def create(
        title: str,
        description: str,
        severity: str,
        location: str,
    ) -> Incident:
        """
        Create a new incident.
        """
        incident = Incident(
            title=title,
            description=description,
            severity=severity,
            location=location,
        )

        db.session.add(incident)
        db.session.commit()

        return incident

    @staticmethod
    def search(keyword: str) -> list[Incident]:
        """
        Return incidents whose title, description or location matches.

        The keyword is matched case-insensitively anywhere in the field.
        """
        pattern = f"%{keyword}%"

        return (
            Incident.query
            .filter(
                db.or_(
                    Incident.title.ilike(pattern),
                    Incident.description.ilike(pattern),
                    Incident.location.ilike(pattern),
                )
            )
            .order_by(Incident.created_at.desc())
            .all()
        )