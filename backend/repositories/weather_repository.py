"""
Database access layer for WeatherReport entities.
"""

from database import db
from models.weather_report import WeatherReport


class WeatherRepository:
    """Repository for weather report database operations."""

    @staticmethod
    def get_all() -> list[WeatherReport]:
        """
        Return all weather reports, newest first.
        """
        return (
            WeatherReport.query
            .order_by(WeatherReport.created_at.desc())
            .all()
        )

    @staticmethod
    def get_latest() -> WeatherReport | None:
        """
        Return the most recent weather report.
        """
        return (
            WeatherReport.query
            .order_by(WeatherReport.created_at.desc())
            .first()
        )

    @staticmethod
    def create(
        condition: str,
        visibility: float,
        wind_speed: float,
        temperature: float,
    ) -> WeatherReport:
        """
        Create a new weather report.
        """
        report = WeatherReport(
            condition=condition,
            visibility=visibility,
            wind_speed=wind_speed,
            temperature=temperature,
        )

        db.session.add(report)
        db.session.commit()

        return report