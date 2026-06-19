from datetime import datetime, timezone

from database import db


class WeatherReport(db.Model):
    __tablename__ = "weather_reports"

    id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.String(80), nullable=False)
    visibility = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "condition": self.condition,
            "visibility": self.visibility,
            "wind_speed": self.wind_speed,
            "temperature": self.temperature,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
