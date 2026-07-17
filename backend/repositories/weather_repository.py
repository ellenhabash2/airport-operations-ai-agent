"""
Database access layer for WeatherReport entities.
"""

from models.weather_report import WeatherReport


class WeatherRepository:
    """Repository for weather report database operations."""

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