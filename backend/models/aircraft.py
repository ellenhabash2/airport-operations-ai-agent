from database import db


class Aircraft(db.Model):
    __tablename__ = "aircraft"

    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    aircraft_type = db.Column(db.String(80), nullable=False)
    airline_id = db.Column(db.Integer, db.ForeignKey("airlines.id"), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="available")

    airline = db.relationship("Airline", back_populates="aircraft")
    flights = db.relationship("Flight", back_populates="aircraft", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "registration_number": self.registration_number,
            "aircraft_type": self.aircraft_type,
            "airline_id": self.airline_id,
            "airline": self.airline.name if self.airline else None,
            "status": self.status,
        }
